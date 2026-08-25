import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "demo").lower()
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./smartwms_demo.db")
    chat_message_max_length: int = int(os.getenv("CHAT_MESSAGE_MAX_LENGTH", "2000"))
    oci_region: str | None = os.getenv("OCI_REGION") or None
    oci_compartment_id: str | None = os.getenv("OCI_COMPARTMENT_ID") or None
    oci_project_id: str | None = os.getenv("OCI_PROJECT_ID") or None
    oci_genai_endpoint: str | None = os.getenv("OCI_GENAI_ENDPOINT") or None

    @property
    def demo_mode(self) -> bool:
        return self.app_env != "oci"


settings = Settings()
