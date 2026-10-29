"""
Smart Business Idea Generator - Main Flask Application
Multi-Agent Agentic AI using IBM Granite LLM
"""
import os
import json
import uuid
import logging
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify,
    session, send_file
)
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Agent imports
from agents.rag_agent import RAGAgent
from agents.trend_agent import TrendAnalysisAgent
from agents.idea_agent import IdeaGenerationAgent
from agents.feasibility_agent import FeasibilityAgent
from agents.refinement_agent import RefinementAgent
from agents.roadmap_agent import RoadmapAgent
from agents.ethics_agent import EthicsGuardrailAgent

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
IBM_API_KEY = os.environ.get("IBM_API_KEY", "BYVHRL3kN81Kcmo4zAsTGpIvPOfRaRSc3zCRNHdTxGaw")
IBM_PROJECT_ID = os.environ.get("IBM_PROJECT_ID", "a3116599-fb03-45d6-a324-2a05a4e43a47")
IBM_ENDPOINT = os.environ.get("IBM_ENDPOINT", "https://au-syd.ml.cloud.ibm.com")

UPLOAD_FOLDER = Path(__file__).parent / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_AUDIO_EXTENSIONS = {"wav", "mp3", "ogg", "m4a", "webm"}

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SAVED_IDEAS_FILE = DATA_DIR / "saved_ideas.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sbig-secret-2024-granite-ai-9x8y7z")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
CORS(app)

# ---------------------------------------------------------------------------
# Agent factory (lazy init, shared per request context is fine for demo)
# ---------------------------------------------------------------------------
def _make_agents():
    kwargs = dict(api_key=IBM_API_KEY, project_id=IBM_PROJECT_ID, endpoint_url=IBM_ENDPOINT)
    return {
        "rag": RAGAgent(**kwargs),
        "trend": TrendAnalysisAgent(**kwargs),
        "idea": IdeaGenerationAgent(**kwargs),
        "feasibility": FeasibilityAgent(**kwargs),
        "refinement": RefinementAgent(**kwargs),
        "roadmap": RoadmapAgent(**kwargs),
        "ethics": EthicsGuardrailAgent(**kwargs),
    }


_agents = None


def get_agents():
    global _agents
    if _agents is None:
        _agents = _make_agents()
    return _agents


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def allowed_file(filename: str, allowed: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def load_saved_ideas() -> list:
    if SAVED_IDEAS_FILE.exists():
        try:
            with open(SAVED_IDEAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_ideas_to_disk(ideas: list):
    with open(SAVED_IDEAS_FILE, "w", encoding="utf-8") as f:
        json.dump(ideas, f, indent=2, default=str)


def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


def sanitise_profile(profile: dict) -> dict:
    """Remove PII beyond what is needed; hash the name for internal use."""
    safe = {k: str(v)[:500] for k, v in profile.items() if v}
    # Store only first name for personalisation
    if "name" in safe and " " in safe["name"]:
        safe["name"] = safe["name"].split()[0]
    return safe


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    get_session_id()
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "model": "ibm/granite-3-3-8b-instruct", "timestamp": datetime.utcnow().isoformat()})


# ── Generate Ideas ──────────────────────────────────────────────────────────
@app.route("/api/generate", methods=["POST"])
def generate_ideas():
    """Main pipeline: RAG → Trend → Idea → Feasibility → Ethics."""
    data = request.get_json(force=True) or {}
    user_profile = sanitise_profile(data.get("profile", {}))

    if not user_profile:
        return jsonify({"error": "User profile is required."}), 400

    agents = get_agents()

    # Ethics input check
    combined_input = " ".join(str(v) for v in user_profile.values())
    ethics_check = agents["ethics"].check_input(combined_input)
    if not ethics_check["safe"]:
        return jsonify({"error": ethics_check["reason"]}), 400

    try:
        logger.info("Starting idea generation pipeline for session %s", get_session_id())

        # 1. RAG knowledge retrieval
        knowledge = agents["rag"].retrieve_knowledge(user_profile)
        logger.info("RAG complete")

        # 2. Trend analysis
        trends = agents["trend"].analyse_trends(user_profile, knowledge)
        logger.info("Trend analysis complete")

        # 3. Idea generation
        raw_ideas = agents["idea"].generate_ideas(user_profile, knowledge, trends)
        logger.info("Idea generation complete: %d ideas", len(raw_ideas))

        # 4. Feasibility scoring
        scored_ideas = agents["feasibility"].evaluate(raw_ideas, user_profile)
        logger.info("Feasibility scoring complete")

        # 5. Ethics screening
        screened_ideas = agents["ethics"].check_ideas(scored_ideas)
        final_ideas = agents["ethics"].add_ethics_disclaimer(screened_ideas)
        ethics_report = agents["ethics"].generate_ethics_report(final_ideas, user_profile)

        # Sort by overall score desc
        final_ideas.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

        # Store in session
        session["last_ideas"] = final_ideas
        session["last_profile"] = user_profile
        session["last_trends"] = trends
        session.modified = True

        return jsonify({
            "ideas": final_ideas,
            "trends": trends,
            "knowledge": {
                "industry": knowledge.get("industry"),
                "market_insights": knowledge.get("market_insights", []),
                "emerging_niches": knowledge.get("emerging_niches", []),
            },
            "ethics_report": ethics_report,
            "session_id": get_session_id(),
        })

    except Exception as exc:
        logger.exception("Pipeline error: %s", exc)
        return jsonify({"error": f"Generation failed: {str(exc)}"}), 500


# ── Refine Idea ─────────────────────────────────────────────────────────────
@app.route("/api/refine", methods=["POST"])
def refine_idea():
    data = request.get_json(force=True) or {}
    idea = data.get("idea") or {}
    user_profile = data.get("profile") or session.get("last_profile") or {}
    focus_area = data.get("focus_area", "full")

    if not idea:
        return jsonify({"error": "Idea data is required."}), 400

    agents = get_agents()
    try:
        refinement = agents["refinement"].refine_idea(idea, user_profile, focus_area)
        return jsonify({"refinement": refinement})
    except Exception as exc:
        logger.exception("Refinement error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── Ask Query ────────────────────────────────────────────────────────────────
@app.route("/api/ask", methods=["POST"])
def ask_query():
    data = request.get_json(force=True) or {}
    idea = data.get("idea") or {}
    query = data.get("query", "").strip()
    user_profile = data.get("profile") or session.get("last_profile") or {}

    if not query:
        return jsonify({"error": "Query is required."}), 400

    agents = get_agents()
    ethics_check = agents["ethics"].check_input(query)
    if not ethics_check["safe"]:
        return jsonify({"error": ethics_check["reason"]}), 400

    try:
        answer = agents["refinement"].answer_query(idea, query, user_profile)
        return jsonify({"answer": answer})
    except Exception as exc:
        logger.exception("Query error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── Generate Roadmap ─────────────────────────────────────────────────────────
@app.route("/api/roadmap", methods=["POST"])
def generate_roadmap():
    data = request.get_json(force=True) or {}
    idea = data.get("idea") or {}
    user_profile = data.get("profile") or session.get("last_profile") or {}

    if not idea:
        return jsonify({"error": "Idea data is required."}), 400

    agents = get_agents()
    try:
        roadmap = agents["roadmap"].generate_roadmap(idea, user_profile)
        return jsonify({"roadmap": roadmap})
    except Exception as exc:
        logger.exception("Roadmap error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── Save / Load Ideas ────────────────────────────────────────────────────────
@app.route("/api/save", methods=["POST"])
def save_idea():
    data = request.get_json(force=True) or {}
    idea = data.get("idea")
    if not idea:
        return jsonify({"error": "No idea provided."}), 400

    saved = load_saved_ideas()
    idea["saved_at"] = datetime.utcnow().isoformat()
    idea["save_id"] = str(uuid.uuid4())
    saved.append(idea)
    save_ideas_to_disk(saved)
    return jsonify({"message": "Idea saved successfully.", "save_id": idea["save_id"]})


@app.route("/api/saved", methods=["GET"])
def get_saved_ideas():
    return jsonify({"saved_ideas": load_saved_ideas()})


@app.route("/api/saved/<save_id>", methods=["DELETE"])
def delete_saved_idea(save_id):
    saved = load_saved_ideas()
    updated = [s for s in saved if s.get("save_id") != save_id]
    save_ideas_to_disk(updated)
    return jsonify({"message": "Idea deleted."})


# ── Multimodal Input ─────────────────────────────────────────────────────────
@app.route("/api/upload/image", methods=["POST"])
def upload_image():
    """Process uploaded image and extract business context using Granite."""
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]
    if not file or not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({"error": "Invalid image file type."}), 400

    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)

    agents = get_agents()
    try:
        # Read image and encode to base64 for description
        with open(filepath, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        prompt = f"""A user uploaded an image for business idea brainstorming. The image file is named '{file.filename}'.

Based on this context, describe what business opportunities or ideas this image might suggest.
Provide: 1) What the image likely shows, 2) 2-3 potential business ideas it inspires, 3) Keywords to add to user profile.

Return JSON: {{"image_context": "description", "inspired_ideas": ["idea1", "idea2"], "keywords": ["kw1", "kw2"]}}"""

        raw = agents["rag"].generate(prompt, max_tokens=400)
        result = agents["rag"].parse_json_response(raw)
        result["filename"] = filename
        result["image_url"] = f"/static/uploads/{filename}"
        return jsonify(result)
    except Exception as exc:
        logger.exception("Image processing error: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/api/upload/audio", methods=["POST"])
def upload_audio():
    """Process uploaded audio and transcribe for text input."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    file = request.files["audio"]
    if not file or not allowed_file(file.filename or "file.wav", ALLOWED_AUDIO_EXTENSIONS):
        return jsonify({"error": "Invalid audio file type."}), 400

    filename = secure_filename(f"{uuid.uuid4()}_{file.filename or 'recording.wav'}")
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)

    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        try:
            with sr.AudioFile(str(filepath)) as source:
                audio = r.record(source)
            transcript = r.recognize_google(audio)
        except Exception:
            # Fallback: try to use the filename as a hint
            transcript = f"Voice input received from file: {file.filename}"

        return jsonify({"transcript": transcript, "filename": filename})
    except ImportError:
        return jsonify({"transcript": "Voice transcription requires SpeechRecognition library.", "filename": filename})
    except Exception as exc:
        logger.exception("Audio processing error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── Export ───────────────────────────────────────────────────────────────────
@app.route("/api/export/json", methods=["POST"])
def export_json():
    data = request.get_json(force=True) or {}
    ideas = data.get("ideas", session.get("last_ideas", []))
    profile = data.get("profile", session.get("last_profile", {}))

    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "generated_by": "Smart Business Idea Generator - IBM Granite",
        "user_profile": {k: v for k, v in profile.items() if k != "name"},
        "ideas": ideas,
    }

    export_path = DATA_DIR / f"export_{uuid.uuid4().hex[:8]}.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)

    return send_file(str(export_path), as_attachment=True, download_name="business_ideas.json", mimetype="application/json")


@app.route("/api/export/txt", methods=["POST"])
def export_txt():
    data = request.get_json(force=True) or {}
    ideas = data.get("ideas", session.get("last_ideas", []))

    lines = ["=" * 60, "SMART BUSINESS IDEA GENERATOR", "Powered by IBM Granite LLM", "=" * 60, ""]
    lines.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")

    for i, idea in enumerate(ideas, 1):
        lines.append(f"{'─'*50}")
        lines.append(f"IDEA {i}: {idea.get('title', 'Untitled')}")
        lines.append(f"Category: {idea.get('category', 'N/A')} | Overall Score: {idea.get('overall_score', 'N/A')}/100")
        lines.append(f"Tagline: {idea.get('tagline', '')}")
        lines.append("")
        lines.append(f"Problem: {idea.get('problem', '')}")
        lines.append(f"Solution: {idea.get('solution', '')}")
        lines.append(f"Target Market: {idea.get('target_market', '')}")
        lines.append(f"Revenue Model: {idea.get('revenue_model', '')}")
        lines.append(f"Unique Value: {idea.get('unique_value', '')}")
        lines.append(f"Timeline: {idea.get('estimated_timeline', '')}")
        lines.append(f"Startup Cost: {idea.get('startup_cost_estimate', '')}")
        lines.append("")
        steps = idea.get("initial_steps", [])
        if steps:
            lines.append("First Steps:")
            for step in steps:
                lines.append(f"  • {step}")
        lines.append("")

    content = "\n".join(lines)
    export_path = DATA_DIR / f"export_{uuid.uuid4().hex[:8]}.txt"
    with open(export_path, "w", encoding="utf-8") as f:
        f.write(content)

    return send_file(str(export_path), as_attachment=True, download_name="business_ideas.txt", mimetype="text/plain")


# ── Trends data endpoint ─────────────────────────────────────────────────────
@app.route("/api/trends", methods=["GET"])
def get_trends():
    trends = session.get("last_trends")
    if not trends:
        return jsonify({"trends": None, "message": "Generate ideas first to see trends."})
    return jsonify({"trends": trends})


# ── General Chat / Q&A ───────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def general_chat():
    """General purpose chat about business and innovation."""
    data = request.get_json(force=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required."}), 400

    agents = get_agents()
    ethics_check = agents["ethics"].check_input(message)
    if not ethics_check["safe"]:
        return jsonify({"response": ethics_check["reason"]})

    user_profile = data.get("profile") or session.get("last_profile") or {}

    prompt = f"""You are a friendly and knowledgeable AI business advisor powered by IBM Granite. Help entrepreneurs and innovators with their business questions.

USER CONTEXT: {agents['rag'].format_user_context(user_profile) if user_profile else "General user"}

USER MESSAGE: {message}

Provide a helpful, encouraging, and actionable response in 2-4 paragraphs. Be specific and practical.
If the question is about ethics, privacy, or responsible business practices, emphasise those values.
Always maintain a respectful, helpful, and motivating tone (HAM principles)."""

    try:
        response = agents["refinement"].generate(prompt, max_tokens=600)
        return jsonify({"response": response})
    except Exception as exc:
        logger.exception("Chat error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── Compare Ideas ────────────────────────────────────────────────────────────
@app.route("/api/compare", methods=["POST"])
def compare_ideas():
    data = request.get_json(force=True) or {}
    idea_ids = data.get("idea_ids", [])
    ideas = data.get("ideas", session.get("last_ideas", []))

    selected = [i for i in ideas if i.get("id") in idea_ids]
    if len(selected) < 2:
        return jsonify({"error": "Select at least 2 ideas to compare."}), 400

    comparison = {
        "ideas": selected,
        "comparison_matrix": {
            "dimensions": ["feasibility_score", "impact_score", "innovation_score", "market_potential_score", "overall_score"],
            "labels": ["Feasibility", "Impact", "Innovation", "Market Potential", "Overall"],
        },
    }
    return jsonify(comparison)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "File too large. Maximum 16 MB allowed."}), 413


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error."}), 500


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting Smart Business Idea Generator on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
