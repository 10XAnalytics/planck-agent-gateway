"""
QUANTA-VIGIL Handler — Quantum Integrity Monitoring
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

Handles collapsed decisions from the integrity_monitor grammar.
Maps symbolic states to operational VIGIL actions:

    SECURE     → pass (integrity confirmed)
    DEGRADED   → warn + checkpoint
    BREACHED   → lockdown + forensics
    RESTORING  → recovery mode + integrity rebuild
"""

from ..handler import BaseHandler, HandlerResult


_SEVERITY = {
    "SECURE":    "INFO",
    "DEGRADED":  "WARNING",
    "BREACHED":  "CRITICAL",
    "RESTORING": "WARNING",
}

_ACTION = {
    "SECURE":    "integrity_confirmed",
    "DEGRADED":  "warn_and_checkpoint",
    "BREACHED":  "lockdown_and_forensics",
    "RESTORING": "recovery_mode",
}

_ALERT_SYMBOLS = {"BREACHED", "DEGRADED"}


class VigilHandler(BaseHandler):
    """
    QUANTA-VIGIL: Integrity monitoring handler.

    Processes collapsed integrity_monitor grammar decisions and
    emits structured VIGIL operational responses.
    """

    name = "QUANTA-VIGIL"

    def can_handle(self, grammar: str) -> bool:
        return grammar in ("integrity_monitor", "vigil")

    def handle(self, decision: dict) -> HandlerResult:
        symbol = decision.get("symbol", "SECURE")
        entropy_signal = decision.get("entropy_signal", 0.0)
        agent_id = decision.get("agent_id", "unknown")
        payload = decision.get("payload", {})

        action = _ACTION.get(symbol, "integrity_confirmed")
        severity = _SEVERITY.get(symbol, "INFO")
        alert = symbol in _ALERT_SYMBOLS

        data = {
            "agent_id":        agent_id,
            "integrity_score": 1.0 - decision.get("value", 0.0),  # inverted: 0=breach, 1=secure
            "entropy_signal":  entropy_signal,
            "swarm_size":      decision.get("swarm_size", 1),
            "vigil_action":    action,
        }
        if payload:
            data["context"] = payload

        # Forensics metadata for BREACHED state
        if symbol == "BREACHED":
            data["forensics"] = {
                "isolate_system":    True,
                "capture_memory":    True,
                "notify_ir_team":    True,
                "preserve_logs":     True,
            }

        # Recovery metadata for RESTORING state
        if symbol == "RESTORING":
            data["recovery"] = {
                "integrity_rebuild": True,
                "verify_checksums":  True,
                "incremental_restore": True,
            }

        return HandlerResult(
            handler=self.name,
            symbol=symbol,
            action=action,
            data=data,
            alert=alert,
            severity=severity,
        )
