"""
QUANTA-RAD Handler — Quantum Radiation / Anomaly Detection
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

QUANTA-RAD extends PULSE with radiometric anomaly detection —
designed for RF spectrum, signal intelligence, and sensor fusion.
Uses the same threat_detection grammar but applies RAD-specific
operational responses focused on signal classification.

    NOMINAL   → baseline signal (no action)
    ANOMALOUS → flag spectral anomaly
    SPOOFED   → classify as spoofed/synthetic signal
    CONFIRMED → confirmed hostile signal — jam/null/report
    RESOLVED  → signal cleared, return to baseline
"""

from ..handler import BaseHandler, HandlerResult


_SEVERITY = {
    "NOMINAL":   "INFO",
    "ANOMALOUS": "WARNING",
    "SPOOFED":   "WARNING",
    "CONFIRMED": "CRITICAL",
    "RESOLVED":  "INFO",
}

_ACTION = {
    "NOMINAL":   "baseline_monitor",
    "ANOMALOUS": "flag_spectral_anomaly",
    "SPOOFED":   "classify_synthetic_signal",
    "CONFIRMED": "report_hostile_signal",
    "RESOLVED":  "return_to_baseline",
}

_ALERT_SYMBOLS = {"SPOOFED", "CONFIRMED"}


class RadHandler(BaseHandler):
    """
    QUANTA-RAD: RF/signal anomaly detection handler.

    Processes collapsed threat_detection grammar decisions and
    emits RAD-specific operational responses for signal intelligence.
    """

    name = "QUANTA-RAD"

    def can_handle(self, grammar: str) -> bool:
        return grammar in ("rad", "rf_detection")

    def handle(self, decision: dict) -> HandlerResult:
        symbol = decision.get("symbol", "NOMINAL")
        entropy_signal = decision.get("entropy_signal", 0.0)
        agent_id = decision.get("agent_id", "unknown")
        payload = decision.get("payload", {})

        action = _ACTION.get(symbol, "baseline_monitor")
        severity = _SEVERITY.get(symbol, "INFO")
        alert = symbol in _ALERT_SYMBOLS

        data = {
            "agent_id":        agent_id,
            "signal_entropy":  entropy_signal,
            "threat_value":    decision.get("value", 0.0),
            "swarm_size":      decision.get("swarm_size", 1),
            "rad_action":      action,
        }
        if payload:
            data["signal_metadata"] = payload

        if symbol == "CONFIRMED":
            data["signal_response"] = {
                "report_to_c2":   True,
                "log_frequency":  payload.get("frequency", "unknown"),
                "classify_emitter": True,
            }

        return HandlerResult(
            handler=self.name,
            symbol=symbol,
            action=action,
            data=data,
            alert=alert,
            severity=severity,
        )
