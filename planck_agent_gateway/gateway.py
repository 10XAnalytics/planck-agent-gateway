"""
planck-agent-gateway — Planck Gateway
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

The PlanckGateway is the primary entry point for routing collapsed
agent decisions from seraphim-logic-core into QUANTA operational systems.

It sits at the boundary between the sub-Planck symbolic layer and the
QUANTA operational layer:

    seraphim-logic-core (quantum collapse)
           ↓
    PlanckGateway (routing + dispatch)
           ↓
    QUANTA Handlers (PULSE / VIGIL / RAD / SRD / ...)

All decisions pass through the gateway as structured dicts.
The gateway routes, handles, logs, and optionally dispatches alerts.
"""

import time
import logging
from typing import Callable, List, Optional

from .router import DecisionRouter
from .handler import HandlerResult

logger = logging.getLogger("planck_agent_gateway")


class PlanckGateway:
    """
    Primary routing gateway for collapsed Seraphim agent decisions.

    Features:
        - Automatic routing to QUANTA product handlers
        - Decision log (in-memory, bounded)
        - Alert callback support
        - Swarm batch processing
    """

    def __init__(
        self,
        alert_callback: Optional[Callable[[HandlerResult], None]] = None,
        log_size: int = 1000,
    ):
        self.router = DecisionRouter()
        self.alert_callback = alert_callback
        self._log: List[dict] = []
        self._log_size = log_size
        self._stats = {
            "total_decisions": 0,
            "total_alerts":    0,
            "by_handler":      {},
            "by_symbol":       {},
        }

    # ── Core dispatch ─────────────────────────────────────────────────────────

    def dispatch(self, decision: dict) -> HandlerResult:
        """
        Route and handle a single collapsed agent decision.

        Args:
            decision: Collapsed state dict from seraphim-logic-core

        Returns:
            HandlerResult from the matched QUANTA handler
        """
        result = self.router.route(decision)

        # Update stats
        self._stats["total_decisions"] += 1
        h = result.handler
        s = result.symbol
        self._stats["by_handler"][h] = self._stats["by_handler"].get(h, 0) + 1
        self._stats["by_symbol"][s]  = self._stats["by_symbol"].get(s, 0) + 1

        # Log result
        entry = {**result.to_dict(), "decision": decision}
        self._log.append(entry)
        if len(self._log) > self._log_size:
            self._log.pop(0)

        # Fire alert callback
        if result.alert:
            self._stats["total_alerts"] += 1
            logger.warning(
                "[%s] ALERT — %s → %s (entropy=%.3f)",
                result.handler,
                result.symbol,
                result.action,
                decision.get("entropy_signal", 0.0),
            )
            if self.alert_callback:
                self.alert_callback(result)
        else:
            logger.debug(
                "[%s] %s → %s",
                result.handler,
                result.symbol,
                result.action,
            )

        return result

    def dispatch_many(self, decisions: List[dict]) -> List[HandlerResult]:
        """Dispatch a batch of decisions (e.g. from a swarm run)."""
        return [self.dispatch(d) for d in decisions]

    def dispatch_swarm_verdict(self, verdict: dict) -> HandlerResult:
        """
        Dispatch an aggregated swarm verdict.
        Equivalent to dispatch() but logs it as a swarm event.
        """
        verdict = {**verdict, "_source": "swarm_verdict"}
        return self.dispatch(verdict)

    # ── Router access ─────────────────────────────────────────────────────────

    def register_handler(self, handler) -> "PlanckGateway":
        """Register a custom QUANTA handler with the router."""
        self.router.register(handler)
        return self

    # ── Observability ─────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return gateway statistics."""
        return {**self._stats}

    def alerts(self) -> List[dict]:
        """Return all logged alert entries."""
        return [e for e in self._log if e.get("alert")]

    def recent(self, n: int = 10) -> List[dict]:
        """Return the n most recent log entries."""
        return self._log[-n:]

    def reset_log(self) -> None:
        """Clear the decision log."""
        self._log.clear()

    def reset_stats(self) -> None:
        """Reset all statistics."""
        self._stats = {
            "total_decisions": 0,
            "total_alerts":    0,
            "by_handler":      {},
            "by_symbol":       {},
        }

    def __repr__(self) -> str:
        return (
            f"PlanckGateway("
            f"decisions={self._stats['total_decisions']}, "
            f"alerts={self._stats['total_alerts']}, "
            f"handlers={self.router.registered_handlers()})"
        )
