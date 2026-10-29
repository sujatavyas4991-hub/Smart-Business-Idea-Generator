"""RAG Agent: Retrieves domain knowledge to ground idea generation."""
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE = {
    "technology": {
        "trends": ["AI/ML automation", "Edge computing", "Web3/blockchain", "Quantum computing", "AR/VR/XR", "Green tech", "Cybersecurity"],
        "opportunities": ["No-code tools", "API-first businesses", "SaaS platforms", "Developer tools", "AI-powered services"],
        "challenges": ["High R&D costs", "Talent scarcity", "Rapid obsolescence", "Regulatory uncertainty"],
    },
    "healthcare": {
        "trends": ["Telehealth", "Personalised medicine", "Mental health tech", "Wearables", "AI diagnostics", "Elder care tech"],
        "opportunities": ["Remote patient monitoring", "Health data platforms", "Preventive care apps", "Medical supply chain"],
        "challenges": ["HIPAA compliance", "High barriers to entry", "Long approval cycles"],
    },
    "education": {
        "trends": ["Microlearning", "Gamification", "AI tutors", "Skills-based credentialing", "Corporate L&D", "EdTech platforms"],
        "opportunities": ["Upskilling platforms", "STEM tools", "Language learning", "Vocational training"],
        "challenges": ["Engagement retention", "Monetisation", "Accreditation"],
    },
    "finance": {
        "trends": ["Embedded finance", "DeFi", "Open banking", "BNPL", "ESG investing", "RegTech"],
        "opportunities": ["Neobanks", "Payment solutions", "Financial literacy tools", "SME lending"],
        "challenges": ["Regulatory compliance", "Trust building", "Security"],
    },
    "retail": {
        "trends": ["Social commerce", "D2C brands", "Sustainable products", "Hyper-personalisation", "Omnichannel retail"],
        "opportunities": ["Niche e-commerce", "Subscription boxes", "Resale platforms", "Local artisan marketplaces"],
        "challenges": ["Logistics costs", "Competition from giants", "Customer acquisition"],
    },
    "food": {
        "trends": ["Plant-based food", "Ghost kitchens", "Food delivery", "Functional foods", "Zero-waste packaging"],
        "opportunities": ["Health-focused brands", "Meal kit services", "Food waste reduction", "Farm-to-table"],
        "challenges": ["Perishability", "Thin margins", "Food safety regulations"],
    },
    "sustainability": {
        "trends": ["Circular economy", "Carbon markets", "Clean energy", "Sustainable fashion", "ESG reporting"],
        "opportunities": ["Green products", "Carbon offset platforms", "Eco-consulting", "Renewable energy solutions"],
        "challenges": ["Higher costs", "Consumer scepticism", "Supply chain complexity"],
    },
    "general": {
        "trends": ["Remote work tools", "Creator economy", "Gig platforms", "Community-led growth", "Micro-SaaS"],
        "opportunities": ["B2B services", "Niche marketplaces", "AI-enhanced workflows", "Automation tools"],
        "challenges": ["Market validation", "Funding access", "Talent acquisition"],
    },
}


class RAGAgent(BaseAgent):
    """Retrieves relevant industry knowledge to augment idea generation."""

    def retrieve_knowledge(self, user_profile: dict) -> dict:
        """Fetch contextual knowledge based on user's industry and interests."""
        industry = (user_profile.get("industry") or "general").lower()
        matched_key = "general"
        for key in KNOWLEDGE_BASE:
            if key in industry or industry in key:
                matched_key = key
                break

        knowledge = KNOWLEDGE_BASE[matched_key].copy()

        # Enrich with LLM-generated context
        context_prompt = f"""You are a business intelligence expert. Given the following user profile, provide 3-5 specific market insights, relevant successful companies, and emerging opportunities as a JSON object with keys: "market_insights" (list), "success_examples" (list), "emerging_niches" (list), "key_statistics" (list of strings).

User Profile:
{self.format_user_context(user_profile)}

Industry Focus: {matched_key}
Known Trends: {', '.join(knowledge.get('trends', []))}

Respond ONLY with valid JSON."""

        try:
            raw = self.generate(context_prompt, max_tokens=800)
            enriched = self.parse_json_response(raw)
            if "raw_response" not in enriched:
                knowledge.update(enriched)
        except Exception as exc:
            logger.warning("RAG enrichment failed: %s", exc)

        knowledge["industry"] = matched_key
        return knowledge
