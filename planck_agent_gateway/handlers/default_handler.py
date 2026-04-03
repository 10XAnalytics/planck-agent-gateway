"""
Default Handler — Unrouted Decision Fallback
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

Catches any collapsed decision that no registered handler claimed.
Logs the decision and emits an INFO-level result. Never raises.
"""

from ..handler import BaseHandler, HandlerResult


class DefaultHandler(BaseHandler):
    """
    Fallback handler for unrecognized grammars.
    Accepts any decision — returns INFO-level result with raw data.
    """

    name = "DEFAULT"

    def can_handle(self, grammar: str) -> bool:
        return True  # always accepts

    def handle(self, decision: dict) -> HandlerResult:
        symbol = decision.get("symbol", "UNKNOWN")
        return HandlerResult(
            handler=self.name,
            symbol=symbol,
            action="log_unrouted_decision",
            data={
                "agent_id":  decision.get("agent_id", "unknown"),
                "grammar":   decision.get("grammar", "unknown"),
                "raw":       decision,
            },
            alert=False,
            severity="INFO",
        )
