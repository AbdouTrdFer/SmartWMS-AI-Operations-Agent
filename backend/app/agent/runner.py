import re
from uuid import uuid4

from app.providers.base import LLMContext, LLMProvider
from app.repositories.wms_repository import WMSRepository
from app.retrieval.base import Retriever
from app.schemas.chat import ChatResponse, Source, ToolCall
from app.tools.wms_tools import ToolResult, WMSTools
from sqlalchemy.orm import Session

SKU_SEARCH = re.compile(r"\bSKU-[0-9A-Z]+\b", re.IGNORECASE)
WAREHOUSE_SEARCH = re.compile(r"\bWH-[0-9A-Z]+\b", re.IGNORECASE)


class AgentRunner:
    def __init__(self, db: Session, llm_provider: LLMProvider, retriever: Retriever):
        repository = WMSRepository(db)
        self.tools = WMSTools(repository)
        self.llm_provider = llm_provider
        self.retriever = retriever

    def run(self, message: str, conversation_id: str | None = None) -> ChatResponse:
        conversation = conversation_id or str(uuid4())
        tool_results = self._run_tools(message)
        retrieved = self._retrieve(message)
        facts = [fact for result in tool_results for fact in result.facts]
        retrieved_notes = [self._summarize_document(doc.text) for doc in retrieved]
        answer = self.llm_provider.generate(
            LLMContext(message=message, facts=facts, retrieved_notes=retrieved_notes)
        )
        return ChatResponse(
            answer=answer,
            tools_used=[ToolCall(name=result.name) for result in tool_results],
            sources=[Source(id=doc.id, title=doc.title) for doc in retrieved],
            conversation_id=conversation,
        )

    def _run_tools(self, message: str) -> list[ToolResult]:
        lowered = message.lower()
        sku = self._extract_sku(message)
        warehouse = self._extract_warehouse(message)
        results: list[ToolResult] = []

        if any(term in lowered for term in ["low stock", "reorder", "stockout", "shortage"]):
            results.append(self.tools.get_low_stock_items(warehouse))
            if sku:
                results.append(self.tools.get_product(sku))
                results.append(self.tools.get_inventory(sku, warehouse))
                results.append(self.tools.get_stock_movements(sku, days=14))
            results.append(self.tools.get_open_orders(warehouse))
            return results

        if "open order" in lowered or "backlog" in lowered:
            return [self.tools.get_open_orders(warehouse)]

        if "movement" in lowered or "recent" in lowered:
            if sku:
                return [self.tools.get_stock_movements(sku, days=14)]

        if any(term in lowered for term in ["inventory", "available", "on hand", "on-hand"]):
            if sku:
                return [self.tools.get_inventory(sku, warehouse)]
            return [self.tools.get_low_stock_items(warehouse)]

        if sku:
            return [self.tools.get_product(sku), self.tools.get_inventory(sku, warehouse)]

        return results

    def _retrieve(self, message: str):
        retrieval_terms = [
            "receiving",
            "damaged",
            "damage",
            "count",
            "cycle",
            "reorder",
            "stockout",
            "escalation",
            "pick",
            "pack",
            "policy",
            "procedure",
            "sop",
        ]
        if any(term in message.lower() for term in retrieval_terms):
            return self.retriever.search(message, limit=3)
        return []

    def _extract_sku(self, message: str) -> str | None:
        match = SKU_SEARCH.search(message)
        return match.group(0).upper() if match else None

    def _extract_warehouse(self, message: str) -> str | None:
        match = WAREHOUSE_SEARCH.search(message)
        return match.group(0).upper() if match else None

    def _summarize_document(self, text: str) -> str:
        lines = [
            line.strip("#- ")
            for line in text.splitlines()
            if line.strip() and not line.startswith(">")
        ]
        return " ".join(lines[:3])[:300]
