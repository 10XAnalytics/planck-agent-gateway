"""
QUANTA-PULSE Handler — Quantum Post-Quantum Threat Detection
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

Handles collapsed decisions from the threat_detection grammar.
Maps symbolic states to operational PULSE actions:

    NOMINAL   → monitor (no action)
    ANOMALOUS → flag + increase scan rate
    SPOOFED   → isolate + alert
    CONFIRMED → escalate + block
    RESOLVED  → clear + resume normal ops
"""

from ..handler import BaseHandler, HandlerResult


# Severity map per symbol
_SEVERITY = {
    "NOMINAL":   "INFO",
    "ANOMALOUS": "WARNING",
    "SPOOFED":   "WARNING",
    "CONFIRMED": "CRITICAL",
    "RESOLVED":  "INFO",
}

# Action map per symbol
_ACTION = {
    "NOMINAL":   "monitor",
    "ANOMALOUS": "flag_and_scan",
    "SPOOFED":   "isolate_and_alert",
    "CONFIRMED": "escalate_and_block",
    "RESOLVED":  "clear_and_resume",
}

_ALERT_SYMBOLS = {"SPOOFED", "CONFIRMED"}


class PulseHandler(BaseHandler):
    """
    QUANTA-PULSE: Quantum-aware threat detection handler.

    Processes collapsed threat_detection grammar decisions and
    emits structured PULSE operational responses.
    """

    name = "QUANTA-PULSE"

    def can_handle(self, grammar: str) -> bool:
        return grammar in ("threat_detection", "pulse")

    def handle(self, decision: dict) -> HandlerResult:
        symbol = decision.get("symbol", "NOMINAL")
        entropy_signal = decision.get("entropy_signal", 0.0)
        agent_id = decision.get("agent_id", "unknown")
        payload = decision.get("payload", {})

        action = _ACTION.get(symbol, "monitor")
        severity = _SEVERITY.get(symbol, "INFO")
        alert = symbol in _ALERT_SYMBOLS

        data = {
            "agent_id":       agent_id,
            "threat_level":   decision.get("value", 0.0),
            "entropy_signal": entropy_signal,
            "swarm_size":     decision.get("swarm_size", 1),
            "swarm_votes":    decision.get("swarm_votes", {}),
            "pulse_action":   action,
        }
        if payload:
            data["context"] = payload

        # Escalation metadata for CONFIRMED threats
        if symbol == "CONFIRMED":
            data["escalation"] = {
                "block_recommended": True,
                "notify_soc": True,
                "preserve_evidence": True,
            }

        return HandlerResult(
            handler=self.name,
            symbol=symbol,
            action=action,
            data=data,
            alert=alert,
            severity=severity,
        )
