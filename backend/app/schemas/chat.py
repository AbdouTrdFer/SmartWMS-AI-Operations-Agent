from app.core.config import settings
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural-language WMS operations question")
    conversation_id: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must not be empty")
        if len(cleaned) > settings.chat_message_max_length:
            raise ValueError(
                f"message must be at most {settings.chat_message_max_length} characters"
            )
        return cleaned


class ToolCall(BaseModel):
    name: str
    status: str = "ok"


class Source(BaseModel):
    id: str
    title: str
    kind: str = "synthetic_policy"


class ChatResponse(BaseModel):
    answer: str
    tools_used: list[ToolCall]
    sources: list[Source]
    conversation_id: str
