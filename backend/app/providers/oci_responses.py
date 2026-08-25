from app.core.config import Settings
from app.providers.base import LLMContext, LLMProvider


class OCIResponsesProvider(LLMProvider):
    """Isolated adapter placeholder for OCI Responses API integration.

    This class intentionally does not implement network behavior or credential loading beyond
    settings validation. Add the official OCI SDK/client calls here when OCI Responses API
    details are introduced for this project.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        missing = [
            name
            for name, value in {
                "OCI_REGION": self.settings.oci_region,
                "OCI_COMPARTMENT_ID": self.settings.oci_compartment_id,
                "OCI_PROJECT_ID": self.settings.oci_project_id,
                "OCI_GENAI_ENDPOINT": self.settings.oci_genai_endpoint,
            }.items()
            if not value
        ]
        if missing:
            joined = ", ".join(missing)
            raise RuntimeError(f"OCI mode is missing required configuration: {joined}")

    def generate(self, context: LLMContext) -> str:
        raise NotImplementedError(
            "OCI Responses API calls are intentionally not implemented in the MVP skeleton."
        )
