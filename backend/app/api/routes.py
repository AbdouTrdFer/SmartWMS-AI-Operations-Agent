from typing import Annotated

from app.agent.runner import AgentRunner
from app.core.config import settings
from app.db.session import get_db
from app.providers.factory import build_llm_provider
from app.retrieval.mock import MockRetriever
from app.schemas.chat import ChatRequest, ChatResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1")
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": settings.app_env}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: DbSession) -> ChatResponse:
    runner = AgentRunner(db=db, llm_provider=build_llm_provider(), retriever=MockRetriever())
    return runner.run(request.message, request.conversation_id)
