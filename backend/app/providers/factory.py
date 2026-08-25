from app.core.config import settings
from app.providers.base import LLMProvider
from app.providers.mock import MockLLMProvider
from app.providers.oci_responses import OCIResponsesProvider


def build_llm_provider() -> LLMProvider:
    if settings.demo_mode:
        return MockLLMProvider()
    return OCIResponsesProvider(settings)
