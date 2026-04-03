"""
planck-agent-gateway — Seraphim Pipeline
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

The SeraphimPipeline wires seraphim-logic-core and planck-agent-gateway
into a single end-to-end operational pipeline:

    Raw data stream / XOR event
         ↓
    AgentSwarm (seraphim-logic-core)
         ↓  quantum collapse + swarm vote
    PlanckGateway (planck-agent-gateway)
         ↓  routing + QUANTA handler dispatch
    HandlerResult → operational action

This is the highest-level interface for integrating Seraphim |LZ⟩
into QUANTA product deployments.
"""

import numpy as np
from typing import Callable, List, Optional

try:
    from seraphim_logic_core import AgentSwarm, SymbolicGrammar
    from seraphim_logic_core import threat_detection_grammar, integrity_grammar
    _SERAPHIM_AVAILABLE = True
except ImportError:
    _SERAPHIM_AVAILABLE = False

from .gateway import PlanckGateway
from .handler import HandlerResult


def _require_seraphim():
    if not _SERAPHIM_AVAILABLE:
        raise ImportError(
            "seraphim-logic-core is required for SeraphimPipeline. "
            "Install it with: pip install seraphim-logic-core"
        )


class SeraphimPipeline:
    """
    End-to-end Seraphim |LZ⟩ → QUANTA pipeline.

    Combines AgentSwarm (quantum collapse) with PlanckGateway (routing)
    into a single callable interface for QUANTA product integrations.

    Usage:
        pipeline = SeraphimPipeline.for_pulse()
        result = pipeline.run_stream(stream_data)
        result = pipeline.run_xor_event(w1, w2)
    """

    def __init__(
        self,
        swarm: "AgentSwarm",
        gateway: Optional[PlanckGateway] = None,
        alert_callback: Optional[Callable[[HandlerResult], None]] = None,
    ):
        _require_seraphim()
        self.swarm = swarm
        self.gateway = gateway or PlanckGateway(alert_callback=alert_callback)

    # ── Factory methods ───────────────────────────────────────────────────────

    @classmethod
    def for_pulse(
        cls,
        use_quantum: bool = True,
        alert_callback: Optional[Callable] = None,
    ) -> "SeraphimPipeline":
        """Create a pipeline configured for QUANTA-PULSE threat detection."""
        _require_seraphim()
        swarm = AgentSwarm(grammar=threat_detection_grammar(), use_quantum=use_quantum)
        return cls(swarm=swarm, alert_callback=alert_callback)

    @classmethod
    def for_vigil(
        cls,
        use_quantum: bool = True,
        alert_callback: Optional[Callable] = None,
    ) -> "SeraphimPipeline":
        """Create a pipeline configured for QUANTA-VIGIL integrity monitoring."""
        _require_seraphim()
        swarm = AgentSwarm(grammar=integrity_grammar(), use_quantum=use_quantum)
        return cls(swarm=swarm, alert_callback=alert_callback)

    @classmethod
    def for_grammar(
        cls,
        grammar: "SymbolicGrammar",
        use_quantum: bool = True,
        alert_callback: Optional[Callable] = None,
    ) -> "SeraphimPipeline":
        """Create a pipeline for any custom SymbolicGrammar."""
        _require_seraphim()
        swarm = AgentSwarm(grammar=grammar, use_quantum=use_quantum)
        return cls(swarm=swarm, alert_callback=alert_callback)

    # ── Run methods ───────────────────────────────────────────────────────────

    def run_stream(
        self,
        stream: np.ndarray,
        payload: Optional[dict] = None,
    ) -> Optional[HandlerResult]:
        """
        Full pipeline from raw data stream.

        1. AgentSwarm detects anomaly and runs agents
        2. Swarm verdict dispatched through PlanckGateway
        3. Returns HandlerResult from matched QUANTA handler

        Returns None if no anomaly detected.
        """
        verdict = self.swarm.respond_to_stream(stream, payload=payload)
        if verdict is None:
            return None
        return self.gateway.dispatch_swarm_verdict(verdict)

    def run_xor_event(
        self,
        w1: np.ndarray,
        w2: np.ndarray,
        payload: Optional[dict] = None,
    ) -> Optional[HandlerResult]:
        """
        Full pipeline from XOR-lattice event (two data windows).

        1. AgentSwarm spawns A = 2^n agents from XOR diff
        2. Agents run lifecycle, swarm votes on verdict
        3. Verdict dispatched through PlanckGateway
        4. Returns HandlerResult from matched QUANTA handler
        """
        verdict = self.swarm.respond_to_xor_event(w1, w2, payload=payload)
        if verdict is None:
            return None
        return self.gateway.dispatch_swarm_verdict(verdict)

    def run_decision(self, decision: dict) -> HandlerResult:
        """
        Dispatch a pre-formed decision dict directly through the gateway.
        Useful when you already have a collapsed agent output.
        """
        return self.gateway.dispatch(decision)

    # ── Observability ─────────────────────────────────────────────────────────

    def stats(self) -> dict:
        return {
            "swarm": self.swarm.status(),
            "gateway": self.gateway.stats(),
        }

    def __repr__(self) -> str:
        return (
            f"SeraphimPipeline("
            f"grammar={self.swarm.grammar.name}, "
            f"quantum={self.swarm.use_quantum})"
        )
