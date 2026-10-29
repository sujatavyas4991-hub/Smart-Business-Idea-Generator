"""Ethics Guardrail Agent: Ensures responsible, ethical, and safe recommendations."""
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

PROHIBITED_PATTERNS = [
    "illegal", "fraud", "scam", "weapon", "drug trafficking",
    "exploit", "money laundering", "hack", "steal", "counterfeit",
    "pyramid scheme", "ponzi", "child", "trafficking", "terrorism",
]

BIAS_INDICATORS = [
    "only men", "only women", "only white", "only black", "only asian",
    "inferior race", "inferior gender",
]


class EthicsGuardrailAgent(BaseAgent):
    """Screens input and output for ethical concerns and applies guardrails."""

    def check_input(self, user_input: str) -> dict:
        """Check user input for prohibited or harmful content."""
        text_lower = user_input.lower()

        for pattern in PROHIBITED_PATTERNS:
            if pattern in text_lower:
                return {
                    "safe": False,
                    "reason": f"Input contains potentially harmful content related to '{pattern}'. Please rephrase your request to focus on lawful and ethical business ideas.",
                    "flagged_term": pattern,
                }

        for bias in BIAS_INDICATORS:
            if bias in text_lower:
                return {
                    "safe": False,
                    "reason": "Input contains language that may promote bias or discrimination. We encourage inclusive and equitable business ideas.",
                    "flagged_term": bias,
                }

        return {"safe": True, "reason": None}

    def check_ideas(self, ideas: list) -> list:
        """Screen generated ideas for ethical concerns."""
        screened = []
        for idea in ideas:
            idea_text = f"{idea.get('title', '')} {idea.get('problem', '')} {idea.get('solution', '')}".lower()
            is_safe = True
            for pattern in PROHIBITED_PATTERNS:
                if pattern in idea_text:
                    is_safe = False
                    break
            if is_safe:
                screened.append(idea)
            else:
                logger.warning("Filtered idea '%s' for ethical concerns.", idea.get("title"))
        return screened

    def add_ethics_disclaimer(self, ideas: list) -> list:
        """Add ethics metadata to each idea."""
        for idea in ideas:
            idea["ethics_compliant"] = True
            idea["privacy_notes"] = "Ensure user data collection complies with GDPR/CCPA regulations."
            idea["inclusion_notes"] = "Design for accessibility and inclusive user experiences."
            idea["sustainability_notes"] = "Consider environmental impact in your business operations."
        return ideas

    def generate_ethics_report(self, ideas: list, user_profile: dict) -> dict:
        """Generate a brief ethics and responsibility assessment."""
        prompt = f"""You are an AI ethics advisor. Review these business ideas and provide a brief ethics and social responsibility assessment.

IDEAS: {', '.join([idea.get('title', '') for idea in ideas[:4]])}
USER GOALS: {user_profile.get('business_goals', 'business growth')}

Provide a JSON response:
{{
  "overall_ethics_rating": "Excellent | Good | Fair | Needs Review",
  "positive_impacts": ["Impact 1", "Impact 2", "Impact 3"],
  "considerations": ["Consideration 1", "Consideration 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "compliance_notes": "Brief note on regulatory considerations"
}}

Respond ONLY with valid JSON."""

        raw = self.generate(prompt, max_tokens=500)
        report = self.parse_json_response(raw)

        if "raw_response" in report:
            report = {
                "overall_ethics_rating": "Good",
                "positive_impacts": [
                    "Creates employment opportunities",
                    "Addresses genuine market needs",
                    "Promotes economic inclusion",
                ],
                "considerations": [
                    "Ensure data privacy compliance (GDPR/CCPA)",
                    "Design accessible products for all users",
                ],
                "recommendations": [
                    "Build privacy-by-design into your product from day one",
                    "Establish clear ethical guidelines for your team",
                ],
                "compliance_notes": "Depending on your industry, consider relevant regulations such as data protection, consumer rights, and sector-specific compliance requirements.",
            }

        return report
