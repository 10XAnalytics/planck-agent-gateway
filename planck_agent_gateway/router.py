"""
planck-agent-gateway — Decision Router
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

The DecisionRouter maps incoming collapsed agent decisions to the correct
QUANTA product handler based on grammar name.

    grammar: "threat_detection" → PulseHandler
    grammar: "integrity_monitor" → VigilHandler
    grammar: "rad" / "rf_detection" → RadHandler
    grammar: <anything else> → DefaultHandler

Handlers are registered by grammar name. Multiple handlers can be
registered for the same grammar — the first match wins.
"""

from typing import Dict, List, Optional
from .handler import BaseHandler, HandlerResult
from .handlers import PulseHandler, VigilHandler, RadHandler, DefaultHandler


class DecisionRouter:
    """
    Routes collapsed agent decisions to the appropriate QUANTA handler.

    Usage:
        router = DecisionRouter()
        result = router.route(decision)
    """

    def __init__(self):
        # Ordered list of handlers — first match wins
        self._handlers: List[BaseHandler] = []
        self._default: BaseHandler = DefaultHandler()

        # Register built-in handlers
        self.register(PulseHandler())
        self.register(VigilHandler())
        self.register(RadHandler())

    def register(self, handler: BaseHandler) -> "DecisionRouter":
        """Register a handler. Later registrations have lower priority."""
        self._handlers.append(handler)
        return self

    def resolve(self, grammar: str) -> BaseHandler:
        """
        Return the first handler that can handle the given grammar.
        Falls back to DefaultHandler if none match.
        """
        for h in self._handlers:
            if h.can_handle(grammar):
                return h
        return self._default

    def route(self, decision: dict) -> HandlerResult:
        """
        Route a collapsed decision dict to the appropriate handler.
        Returns a HandlerResult from the matched handler.
        """
        grammar = decision.get("grammar", "")
        handler = self.resolve(grammar)
        return handler.handle(decision)

    def registered_handlers(self) -> List[str]:
        """Return list of registered handler names."""
        return [h.name for h in self._handlers]

    def __repr__(self) -> str:
        names = ", ".join(self.registered_handlers())
        return f"DecisionRouter(handlers=[{names}])"
