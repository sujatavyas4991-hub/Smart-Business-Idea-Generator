"""Base agent class for all Smart Business Idea Generator agents."""
import json
import logging
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class providing IBM Granite LLM access and shared utilities."""

    MODEL_ID = "ibm/granite-3-3-8b-instruct"

    def __init__(self, api_key: str, project_id: str, endpoint_url: str):
        self.api_key = api_key
        self.project_id = project_id
        self.endpoint_url = endpoint_url
        self._client = None
        self._model = None

    def _get_model(self) -> ModelInference:
        if self._model is None:
            credentials = Credentials(
                url=self.endpoint_url,
                api_key=self.api_key,
            )
            self._client = APIClient(credentials=credentials, project_id=self.project_id)
            self._model = ModelInference(
                model_id=self.MODEL_ID,
                api_client=self._client,
                project_id=self.project_id,
                params={
                    GenParams.MAX_NEW_TOKENS: 2048,
                    GenParams.TEMPERATURE: 0.7,
                    GenParams.TOP_P: 0.9,
                    GenParams.REPETITION_PENALTY: 1.1,
                },
            )
        return self._model

    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Call IBM Granite and return generated text."""
        try:
            model = self._get_model()
            response = model.generate_text(prompt=prompt)
            return response.strip() if response else ""
        except Exception as exc:
            logger.error("LLM generation error: %s", exc)
            return f"[Error generating response: {exc}]"

    def parse_json_response(self, text: str) -> dict:
        """Extract JSON from LLM response, handling markdown fences."""
        try:
            text = text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return {"raw_response": text}

    def format_user_context(self, user_profile: dict) -> str:
        """Create a readable string summary of the user profile."""
        parts = []
        if user_profile.get("name"):
            parts.append(f"Name: {user_profile['name']}")
        if user_profile.get("interests"):
            parts.append(f"Interests: {user_profile['interests']}")
        if user_profile.get("skills"):
            parts.append(f"Skills: {user_profile['skills']}")
        if user_profile.get("budget"):
            parts.append(f"Budget: {user_profile['budget']}")
        if user_profile.get("industry"):
            parts.append(f"Industry: {user_profile['industry']}")
        if user_profile.get("target_audience"):
            parts.append(f"Target Audience: {user_profile['target_audience']}")
        if user_profile.get("business_goals"):
            parts.append(f"Business Goals: {user_profile['business_goals']}")
        if user_profile.get("location"):
            parts.append(f"Location: {user_profile['location']}")
        return "\n".join(parts)
