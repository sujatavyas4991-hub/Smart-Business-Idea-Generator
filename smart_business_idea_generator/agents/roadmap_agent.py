"""Roadmap Agent: Generates actionable innovation roadmaps for selected ideas."""
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RoadmapAgent(BaseAgent):
    """Creates detailed, phased innovation roadmaps for business ideas."""

    def generate_roadmap(self, idea: dict, user_profile: dict) -> dict:
        """Build a comprehensive 12-month innovation roadmap."""
        prompt = f"""You are a startup coach and product strategist. Create a detailed 12-month innovation roadmap for this business idea.

USER PROFILE:
{self.format_user_context(user_profile)}

BUSINESS IDEA:
Title: {idea.get('title')}
Category: {idea.get('category')}
Solution: {idea.get('solution')}
Revenue Model: {idea.get('revenue_model')}
Required Skills: {', '.join(idea.get('required_skills', []))}

Create a JSON roadmap:
{{
  "roadmap_title": "12-Month {idea.get('title')} Roadmap",
  "vision": "One sentence vision statement",
  "phases": [
    {{
      "phase": 1,
      "name": "Foundation (Month 1-3)",
      "theme": "Validate & Build",
      "months": "1-3",
      "objectives": ["Objective 1", "Objective 2"],
      "key_actions": ["Action 1", "Action 2", "Action 3", "Action 4"],
      "deliverables": ["Deliverable 1", "Deliverable 2"],
      "budget_estimate": "$X - $Y",
      "success_metrics": ["Metric 1", "Metric 2"],
      "milestone": "Phase 1 milestone"
    }},
    {{
      "phase": 2,
      "name": "Launch (Month 4-6)",
      "theme": "Go to Market",
      "months": "4-6",
      "objectives": ["Objective 1", "Objective 2"],
      "key_actions": ["Action 1", "Action 2", "Action 3", "Action 4"],
      "deliverables": ["Deliverable 1", "Deliverable 2"],
      "budget_estimate": "$X - $Y",
      "success_metrics": ["Metric 1", "Metric 2"],
      "milestone": "Phase 2 milestone"
    }},
    {{
      "phase": 3,
      "name": "Growth (Month 7-9)",
      "theme": "Scale & Optimise",
      "months": "7-9",
      "objectives": ["Objective 1", "Objective 2"],
      "key_actions": ["Action 1", "Action 2", "Action 3", "Action 4"],
      "deliverables": ["Deliverable 1", "Deliverable 2"],
      "budget_estimate": "$X - $Y",
      "success_metrics": ["Metric 1", "Metric 2"],
      "milestone": "Phase 3 milestone"
    }},
    {{
      "phase": 4,
      "name": "Scale (Month 10-12)",
      "theme": "Expand & Sustain",
      "months": "10-12",
      "objectives": ["Objective 1", "Objective 2"],
      "key_actions": ["Action 1", "Action 2", "Action 3", "Action 4"],
      "deliverables": ["Deliverable 1", "Deliverable 2"],
      "budget_estimate": "$X - $Y",
      "success_metrics": ["Metric 1", "Metric 2"],
      "milestone": "Phase 4 milestone"
    }}
  ],
  "total_budget_estimate": "$X - $Y",
  "key_resources": ["Resource 1", "Resource 2", "Resource 3"],
  "risk_mitigation": ["Risk strategy 1", "Risk strategy 2"],
  "year_2_vision": "What success looks like in year 2"
}}

Be specific, realistic, and tailored to the user's budget and skills.
Respond ONLY with valid JSON."""

        raw = self.generate(prompt, max_tokens=2048)
        roadmap = self.parse_json_response(raw)

        if "raw_response" in roadmap:
            roadmap = self._fallback_roadmap(idea, user_profile)

        return roadmap

    def _fallback_roadmap(self, idea: dict, user_profile: dict) -> dict:
        title = idea.get("title", "Your Business")
        return {
            "roadmap_title": f"12-Month {title} Roadmap",
            "vision": f"Become the go-to solution for {idea.get('target_market', 'our target customers')} within 12 months",
            "phases": [
                {
                    "phase": 1,
                    "name": "Foundation (Month 1-3)",
                    "theme": "Validate & Build",
                    "months": "1-3",
                    "objectives": ["Validate problem-solution fit", "Build core MVP"],
                    "key_actions": [
                        "Conduct 20+ customer discovery interviews",
                        "Define core MVP features (max 5)",
                        "Build prototype / landing page",
                        "Recruit 10 beta testers",
                    ],
                    "deliverables": ["Customer research report", "Working MVP v0.1"],
                    "budget_estimate": "$500 - $3,000",
                    "success_metrics": ["10 beta signups", "3 paying pilot customers"],
                    "milestone": "First paying customer acquired",
                },
                {
                    "phase": 2,
                    "name": "Launch (Month 4-6)",
                    "theme": "Go to Market",
                    "months": "4-6",
                    "objectives": ["Public launch", "First 50 customers"],
                    "key_actions": [
                        "Launch on Product Hunt / social media",
                        "Set up marketing funnel",
                        "Implement feedback loop",
                        "Reach out to 5 potential partners",
                    ],
                    "deliverables": ["Public product launch", "Marketing website"],
                    "budget_estimate": "$1,000 - $5,000",
                    "success_metrics": ["50 active users", "$2K MRR"],
                    "milestone": "50 paying customers",
                },
                {
                    "phase": 3,
                    "name": "Growth (Month 7-9)",
                    "theme": "Scale & Optimise",
                    "months": "7-9",
                    "objectives": ["Optimise conversion", "Expand reach"],
                    "key_actions": [
                        "A/B test pricing and messaging",
                        "Launch referral program",
                        "Explore content marketing / SEO",
                        "Hire first team member",
                    ],
                    "deliverables": ["Referral program", "Content strategy"],
                    "budget_estimate": "$2,000 - $8,000",
                    "success_metrics": ["200 active users", "$5K MRR"],
                    "milestone": "$5K monthly recurring revenue",
                },
                {
                    "phase": 4,
                    "name": "Scale (Month 10-12)",
                    "theme": "Expand & Sustain",
                    "months": "10-12",
                    "objectives": ["Reach profitability", "Plan year 2"],
                    "key_actions": [
                        "Explore enterprise or B2B sales",
                        "Evaluate funding options",
                        "Expand product features based on data",
                        "Build strategic partnerships",
                    ],
                    "deliverables": ["Year 2 plan", "Partnership agreements"],
                    "budget_estimate": "$3,000 - $12,000",
                    "success_metrics": ["500 users", "$10K MRR"],
                    "milestone": "Business profitability / break-even",
                },
            ],
            "total_budget_estimate": "$6,500 - $28,000",
            "key_resources": ["Domain expertise", "Network / advisors", "Digital marketing skills"],
            "risk_mitigation": ["Maintain 3-month cash reserve", "Pivot plan if primary market underperforms"],
            "year_2_vision": "Expand to new markets, build a team of 5, and reach $100K ARR",
        }
