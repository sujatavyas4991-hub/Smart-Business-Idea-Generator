"""Refinement Agent: Deepens and refines a specific idea on user request."""
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RefinementAgent(BaseAgent):
    """Provides in-depth refinement and elaboration of a selected idea."""

    def refine_idea(self, idea: dict, user_profile: dict, focus_area: str = "full") -> dict:
        """Deeply refine and expand a single idea."""
        prompt = f"""You are a seasoned startup mentor and business strategist. Deeply refine and expand the following business idea for this user.

USER PROFILE:
{self.format_user_context(user_profile)}

IDEA TO REFINE:
Title: {idea.get('title')}
Category: {idea.get('category')}
Problem: {idea.get('problem')}
Solution: {idea.get('solution')}
Revenue Model: {idea.get('revenue_model')}
Focus Area: {focus_area}

Provide a comprehensive refinement as JSON:
{{
  "refined_title": "Polished title if needed",
  "elevator_pitch": "90-second pitch script (2-3 paragraphs)",
  "detailed_solution": "Comprehensive solution description (4-5 sentences)",
  "mvp_features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
  "go_to_market": {{
    "phase_1": "0-3 months activities",
    "phase_2": "3-6 months activities", 
    "phase_3": "6-12 months activities"
  }},
  "pricing_strategy": {{
    "model": "Freemium/Subscription/One-time etc",
    "tiers": ["Tier 1: Free - features", "Tier 2: $X/mo - features", "Tier 3: $Y/mo - features"]
  }},
  "partnerships": ["Partner type 1", "Partner type 2", "Partner type 3"],
  "marketing_channels": ["Channel 1", "Channel 2", "Channel 3"],
  "tech_stack": ["Technology 1", "Technology 2"],
  "team_requirements": ["Role 1", "Role 2", "Role 3"],
  "funding_strategy": "Bootstrap/Angel/VC - explanation",
  "year_1_milestones": ["Milestone 1", "Milestone 2", "Milestone 3"],
  "competitive_advantages": ["Advantage 1", "Advantage 2"],
  "pivot_options": ["Alternative direction 1", "Alternative direction 2"]
}}

Make it highly specific to the user's skills, budget, and goals.
Respond ONLY with valid JSON."""

        raw = self.generate(prompt, max_tokens=2048)
        refinement = self.parse_json_response(raw)

        if "raw_response" in refinement:
            refinement = self._fallback_refinement(idea, user_profile)

        return refinement

    def answer_query(self, idea: dict, query: str, user_profile: dict) -> str:
        """Answer a specific user query about an idea."""
        prompt = f"""You are a helpful business advisor. The user is asking about their business idea.

BUSINESS IDEA: {idea.get('title')} - {idea.get('tagline', '')}
Problem: {idea.get('problem', '')}
Solution: {idea.get('solution', '')}

USER QUESTION: {query}

USER PROFILE:
- Skills: {user_profile.get('skills', 'Not specified')}
- Budget: {user_profile.get('budget', 'Not specified')}
- Goals: {user_profile.get('business_goals', 'Not specified')}

Provide a helpful, specific, and actionable answer in 2-4 paragraphs. Be encouraging but realistic."""

        return self.generate(prompt, max_tokens=600)

    def _fallback_refinement(self, idea: dict, user_profile: dict) -> dict:
        title = idea.get("title", "Your Business Idea")
        return {
            "refined_title": title,
            "elevator_pitch": f"{title} addresses a critical market need by providing an innovative solution that combines cutting-edge technology with deep user empathy. Our approach delivers measurable value from day one, with a clear path to sustainable growth and positive impact.",
            "detailed_solution": f"The core solution leverages the founder's expertise in {user_profile.get('skills', 'their domain')} to create a differentiated offering. By focusing on the specific pain points of the target market, we deliver superior results compared to existing alternatives.",
            "mvp_features": ["Core value proposition feature", "User onboarding flow", "Basic analytics dashboard", "Customer support integration", "Mobile-responsive interface"],
            "go_to_market": {
                "phase_1": "Validate with 10-20 beta users, refine product based on feedback",
                "phase_2": "Launch publicly, acquire first 100 paying customers",
                "phase_3": "Scale marketing, explore partnerships, expand features",
            },
            "pricing_strategy": {
                "model": "Freemium with premium tiers",
                "tiers": ["Free: Core features, limited usage", "Pro: $29/month - Full features", "Business: $99/month - Team features + priority support"],
            },
            "partnerships": ["Industry associations", "Complementary software providers", "Local business networks"],
            "marketing_channels": ["Content marketing / SEO", "LinkedIn and social media", "Referral program"],
            "tech_stack": ["Python / React for web app", "AWS or IBM Cloud for hosting"],
            "team_requirements": ["Technical Co-founder or Developer", "Sales / Marketing lead", "Domain expert advisor"],
            "funding_strategy": "Bootstrap with personal savings for MVP, then seek angel investment at traction milestone",
            "year_1_milestones": ["MVP launch within 4 months", "100 paying customers by month 8", "$10K MRR by end of year 1"],
            "competitive_advantages": ["Deep domain expertise", "Faster time-to-value for customers"],
            "pivot_options": ["B2B focus if B2C proves slow", "White-label for established players"],
        }
