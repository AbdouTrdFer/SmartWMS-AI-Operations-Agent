from app.providers.base import LLMContext, LLMProvider


class MockLLMProvider(LLMProvider):
    def generate(self, context: LLMContext) -> str:
        if not context.facts and not context.retrieved_notes:
            return (
                "I can help with inventory, low stock, product details, open orders, "
                "recent stock movements, and WMS policy questions in demo mode."
            )

        parts: list[str] = []
        if context.facts:
            parts.append("Facts from read-only WMS tools:\n- " + "\n- ".join(context.facts))
        if context.retrieved_notes:
            parts.append(
                "Policy context from synthetic documents, "
                "treated as untrusted reference material:\n- "
                + "\n- ".join(context.retrieved_notes)
            )

        recommendation = self._recommendation(context)
        if recommendation:
            parts.append(f"Recommendation: {recommendation}")
        return "\n\n".join(parts)

    def _recommendation(self, context: LLMContext) -> str | None:
        lowered = context.message.lower()
        if (
            "reorder" in lowered
            or "replenishment" in lowered
            or "stockout" in lowered
            or "low stock" in lowered
        ):
            return (
                "Review backend-flagged replenishment candidates first. Confirm counts and "
                "business approvals before any purchasing or transfer action."
            )
        if "damaged" in lowered:
            return (
                "Quarantine damaged goods, record the exception, "
                "and follow supervisor review steps."
            )
        return None
