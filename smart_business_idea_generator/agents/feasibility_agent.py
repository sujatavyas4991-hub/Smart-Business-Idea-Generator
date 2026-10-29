"""Feasibility Evaluation Agent: Scores ideas on multiple dimensions."""
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FeasibilityAgent(BaseAgent):
    """Evaluates feasibility and impact scores for each generated idea."""

    def evaluate(self, ideas: list, user_profile: dict) -> list:
        """Enrich each idea with feasibility scores and evaluation data."""
        budget = user_profile.get("budget", "medium").lower()
        skills = user_profile.get("skills", "")
        goals = user_profile.get("business_goals", "growth")

        ideas_summary = "\n".join(
            [f"Idea {i+1}: {idea.get('title')} - {idea.get('tagline', '')}" for i, idea in enumerate(ideas)]
        )

        prompt = f"""You are a venture capital analyst and business feasibility expert. Evaluate these business ideas for the given user profile.

USER PROFILE:
- Budget: {budget}
- Skills: {skills}
- Goals: {goals}

IDEAS TO EVALUATE:
{ideas_summary}

For each idea, provide scores from 0-100 and analysis. Return a JSON array with one object per idea:
[
  {{
    "idea_index": 0,
    "feasibility_score": 85,
    "impact_score": 78,
    "innovation_score": 72,
    "market_potential_score": 88,
    "risk_score": 45,
    "overall_score": 82,
    "budget_fit": "Low | Medium | High",
    "time_to_revenue": "3-6 months",
    "startup_cost_estimate": "$500 - $5,000",
    "key_risks": ["Risk 1", "Risk 2"],
    "success_factors": ["Factor 1", "Factor 2"],
    "recommendation": "Highly Recommended | Recommended | Consider Carefully | Challenging"
  }}
]

Score conservatively and realistically. Consider the user's budget and skills.
Respond ONLY with valid JSON array."""

        raw = self.generate(prompt, max_tokens=1500)
        evaluations = []

        try:
            parsed = self.parse_json_response(raw)
            if isinstance(parsed, list):
                evaluations = parsed
        except Exception as exc:
            logger.warning("Feasibility parsing failed: %s", exc)

        # Merge evaluations back into ideas
        enriched_ideas = []
        for i, idea in enumerate(ideas):
            eval_data = {}
            for ev in evaluations:
                if isinstance(ev, dict) and ev.get("idea_index") == i:
                    eval_data = ev
                    break

            if not eval_data and i < len(evaluations):
                eval_data = evaluations[i] if isinstance(evaluations[i], dict) else {}

            if not eval_data:
                eval_data = self._default_scores(idea, budget)

            idea["feasibility_score"] = eval_data.get("feasibility_score", 75)
            idea["impact_score"] = eval_data.get("impact_score", 70)
            idea["innovation_score"] = eval_data.get("innovation_score", 72)
            idea["market_potential_score"] = eval_data.get("market_potential_score", 78)
            idea["risk_score"] = eval_data.get("risk_score", 40)
            idea["overall_score"] = eval_data.get("overall_score", 74)
            idea["budget_fit"] = eval_data.get("budget_fit", "Medium")
            idea["time_to_revenue"] = eval_data.get("time_to_revenue", "6-12 months")
            idea["startup_cost_estimate"] = eval_data.get("startup_cost_estimate", "$1,000 - $10,000")
            idea["key_risks"] = eval_data.get("key_risks", ["Market competition", "Funding gaps"])
            idea["success_factors"] = eval_data.get("success_factors", ["Strong execution", "Customer focus"])
            idea["recommendation"] = eval_data.get("recommendation", "Recommended")

            enriched_ideas.append(idea)

        return enriched_ideas

    def _default_scores(self, idea: dict, budget: str) -> dict:
        """Generate sensible default scores based on idea category."""
        category_scores = {
            "Startup": {"feasibility_score": 72, "impact_score": 80, "innovation_score": 75},
            "Product": {"feasibility_score": 68, "impact_score": 73, "innovation_score": 70},
            "Research": {"feasibility_score": 65, "impact_score": 85, "innovation_score": 88},
            "Social Enterprise": {"feasibility_score": 70, "impact_score": 92, "innovation_score": 72},
            "Digital": {"feasibility_score": 82, "impact_score": 75, "innovation_score": 78},
        }
        category = idea.get("category", "Startup")
        scores = category_scores.get(category, {"feasibility_score": 72, "impact_score": 75, "innovation_score": 73})
        scores["market_potential_score"] = 77
        scores["risk_score"] = 38
        scores["overall_score"] = int(sum([scores["feasibility_score"], scores["impact_score"], scores["innovation_score"]]) / 3)
        scores["budget_fit"] = "High" if budget in ["low", "bootstrap"] else "Medium"
        scores["time_to_revenue"] = "6-9 months"
        scores["startup_cost_estimate"] = "$2,000 - $15,000"
        scores["key_risks"] = ["Market saturation", "Customer acquisition cost"]
        scores["success_factors"] = ["Unique value proposition", "Strong network"]
        scores["recommendation"] = "Recommended"
        return scores
