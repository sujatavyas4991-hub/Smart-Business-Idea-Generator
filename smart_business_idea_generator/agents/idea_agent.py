"""Idea Generation Agent: Core agent that produces personalised business ideas."""
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class IdeaGenerationAgent(BaseAgent):
    """Generates personalised, innovative, and actionable business ideas using Granite LLM."""

    def generate_ideas(self, user_profile: dict, knowledge: dict, trends: dict) -> list:
        """Produce 6 diverse, high-quality business ideas."""
        trend_summary = "; ".join(trends.get("hot_trends", [])[:3])
        gaps_summary = "; ".join(trends.get("market_gaps", [])[:3])

        prompt = f"""You are an elite startup advisor and innovation consultant. Based on the detailed user profile and market intelligence below, generate exactly 6 unique, actionable business ideas.

USER PROFILE:
{self.format_user_context(user_profile)}

MARKET INTELLIGENCE:
- Hot Trends: {trend_summary}
- Market Gaps: {gaps_summary}
- Emerging Technologies: {', '.join(trends.get('emerging_technologies', []))}

REQUIREMENTS:
- Generate exactly 6 ideas covering: 2 Startup ideas, 1 Product idea, 1 Research/Innovation idea, 1 Social Enterprise idea, 1 Digital/Online idea
- Each idea must align with the user's budget, skills, and goals
- Ideas must be unique, creative, and immediately actionable
- Focus on the user's specific interests and industry

Return a JSON array with exactly 6 objects. Each object must have:
{{
  "id": "idea_1",
  "title": "Catchy name for the idea",
  "category": "Startup | Product | Research | Social Enterprise | Digital",
  "tagline": "One powerful sentence that captures the essence",
  "problem": "Specific problem this solves",
  "solution": "How this idea solves it",
  "target_market": "Who will use/buy this",
  "revenue_model": "How money is made",
  "unique_value": "What makes this different from competitors",
  "required_skills": ["skill1", "skill2"],
  "initial_steps": ["Step 1", "Step 2", "Step 3"],
  "estimated_timeline": "X months to launch",
  "icon": "emoji representing the idea"
}}

Respond ONLY with a valid JSON array."""

        raw = self.generate(prompt, max_tokens=2048)
        ideas = []

        try:
            parsed = self.parse_json_response(raw)
            if isinstance(parsed, list):
                ideas = parsed
            elif isinstance(parsed, dict) and "raw_response" not in parsed:
                # Try to extract list from dict
                for v in parsed.values():
                    if isinstance(v, list):
                        ideas = v
                        break
        except Exception as exc:
            logger.warning("Idea parsing failed: %s", exc)

        if not ideas:
            ideas = self._fallback_ideas(user_profile)

        # Ensure all ideas have required fields
        for i, idea in enumerate(ideas):
            idea.setdefault("id", f"idea_{i+1}")
            idea.setdefault("icon", "💡")
            idea.setdefault("category", "Startup")
            idea.setdefault("tagline", idea.get("title", "Innovative Idea"))

        return ideas[:6]

    def _fallback_ideas(self, user_profile: dict) -> list:
        """Fallback ideas when LLM parsing fails."""
        industry = user_profile.get("industry", "technology")
        skills = user_profile.get("skills", "problem-solving")
        return [
            {
                "id": "idea_1",
                "title": f"AI-Powered {industry.title()} Consultant",
                "category": "Startup",
                "tagline": f"Democratising expert {industry} advice through AI",
                "problem": f"Small businesses can't afford top {industry} consultants",
                "solution": "AI chatbot providing personalised consulting at fraction of cost",
                "target_market": "SMEs and entrepreneurs",
                "revenue_model": "SaaS subscription $29-$199/month",
                "unique_value": "Domain-specific AI trained on industry best practices",
                "required_skills": [skills, "AI/ML basics", "Domain expertise"],
                "initial_steps": ["Market research", "Build MVP", "Beta test with 10 businesses"],
                "estimated_timeline": "4-6 months to launch",
                "icon": "🤖",
            },
            {
                "id": "idea_2",
                "title": "Skills-to-Income Marketplace",
                "category": "Digital",
                "tagline": "Turn your expertise into recurring income online",
                "problem": "Skilled professionals struggle to monetise niche knowledge",
                "solution": "Platform connecting micro-experts with people needing specific help",
                "target_market": "Freelancers and niche professionals",
                "revenue_model": "15% marketplace commission",
                "unique_value": "Focus on hyper-niche skills ignored by generic platforms",
                "required_skills": ["Platform development", "Community management"],
                "initial_steps": ["Define 5 niche categories", "Build MVP marketplace", "Recruit first 50 experts"],
                "estimated_timeline": "6-8 months to launch",
                "icon": "🛒",
            },
            {
                "id": "idea_3",
                "title": "Sustainable Product Line",
                "category": "Product",
                "tagline": "Eco-friendly products people actually want to use",
                "problem": "Sustainable alternatives are expensive or inconvenient",
                "solution": "Affordable, stylish eco-products for everyday use",
                "target_market": "Environmentally conscious millennials",
                "revenue_model": "D2C e-commerce + retail partnerships",
                "unique_value": "Comparable price to conventional products without sacrificing quality",
                "required_skills": ["Product design", "Supply chain management"],
                "initial_steps": ["Source sustainable suppliers", "Design hero product", "Launch crowdfunding"],
                "estimated_timeline": "8-12 months to first sale",
                "icon": "🌿",
            },
            {
                "id": "idea_4",
                "title": "Community Impact Research Hub",
                "category": "Research",
                "tagline": "Bridging academic research and real-world social impact",
                "problem": "Research findings rarely reach communities that need them most",
                "solution": "Platform translating research into actionable community programs",
                "target_market": "NGOs, local governments, community organisations",
                "revenue_model": "Grant funding + consulting fees",
                "unique_value": "Practical implementation focus vs pure academic output",
                "required_skills": ["Research methodology", "Community engagement"],
                "initial_steps": ["Partner with 2 universities", "Identify 3 pilot communities", "Apply for grants"],
                "estimated_timeline": "12 months to first program",
                "icon": "🔬",
            },
            {
                "id": "idea_5",
                "title": "Digital Upskilling Academy",
                "category": "Social Enterprise",
                "tagline": "Empowering underserved communities with future-ready skills",
                "problem": "Digital divide leaves millions behind in the AI economy",
                "solution": "Affordable micro-courses in digital skills with job placement",
                "target_market": "Career changers and underserved communities",
                "revenue_model": "Freemium + corporate sponsorships + placement fees",
                "unique_value": "Income share agreements align incentives with student success",
                "required_skills": ["Education design", "Corporate partnerships"],
                "initial_steps": ["Build first 3 courses", "Partner with 5 employers", "Launch free cohort"],
                "estimated_timeline": "3-5 months to launch",
                "icon": "🎓",
            },
            {
                "id": "idea_6",
                "title": "Hyper-Local Service Network",
                "category": "Startup",
                "tagline": "Connecting neighbourhoods with trusted local service providers",
                "problem": "Finding reliable local services is time-consuming and risky",
                "solution": "Vetted local professional network with community ratings",
                "target_market": "Homeowners and local service professionals",
                "revenue_model": "Lead generation fees + premium listings",
                "unique_value": "Community-driven trust scores vs anonymous reviews",
                "required_skills": ["Operations", "Marketing", "Community building"],
                "initial_steps": ["Launch in one neighbourhood", "Onboard 20 service providers", "Get first 100 customers"],
                "estimated_timeline": "2-3 months to launch",
                "icon": "🏘️",
            },
        ]
