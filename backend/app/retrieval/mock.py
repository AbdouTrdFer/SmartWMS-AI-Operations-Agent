import re
from pathlib import Path

from app.retrieval.base import RetrievedDocument, Retriever


class MockRetriever(Retriever):
    def __init__(self, knowledge_path: Path | None = None):
        self.knowledge_path = (
            knowledge_path or Path(__file__).resolve().parents[3] / "data" / "knowledge"
        )
        self.documents = self._load_documents()

    def search(self, query: str, limit: int = 3) -> list[RetrievedDocument]:
        query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        ranked: list[RetrievedDocument] = []
        for doc_id, title, text in self.documents:
            terms = set(re.findall(r"[a-z0-9]+", f"{title} {text}".lower()))
            score = float(len(query_terms & terms))
            if score > 0:
                ranked.append(RetrievedDocument(id=doc_id, title=title, text=text, score=score))
        return sorted(ranked, key=lambda item: item.score, reverse=True)[:limit]

    def _load_documents(self) -> list[tuple[str, str, str]]:
        docs: list[tuple[str, str, str]] = []
        for path in sorted(self.knowledge_path.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = text.splitlines()[0].lstrip("# ").strip() if text.splitlines() else path.stem
            docs.append((path.stem, title, text))
        return docs
