"""Tests for QUANTA product handlers."""

import pytest
from planck_agent_gateway.handlers import PulseHandler, VigilHandler, RadHandler, DefaultHandler
from planck_agent_gateway.handler import HandlerResult


def make_decision(grammar, symbol, entropy=0.7, value=0.5, swarm_size=1):
    return {
        "agent_id": "TEST-001",
        "grammar": grammar,
        "symbol": symbol,
        "value": value,
        "entropy_cost": 0.3,
        "information_gain": 0.7,
        "entropy_signal": entropy,
        "lifecycle": "DELIVERED",
        "swarm_size": swarm_size,
        "swarm_votes": {symbol: 3.5},
    }


# ── PulseHandler ──────────────────────────────────────────────────────────────

class TestPulseHandler:
    def setup_method(self):
        self.handler = PulseHandler()

    def test_can_handle_threat_detection(self):
        assert self.handler.can_handle("threat_detection") is True
        assert self.handler.can_handle("pulse") is True
        assert self.handler.can_handle("integrity_monitor") is False

    def test_nominal_no_alert(self):
        result = self.handler.handle(make_decision("threat_detection", "NOMINAL"))
        assert result.alert is False
        assert result.severity == "INFO"
        assert result.action == "monitor"

    def test_anomalous_warning(self):
        result = self.handler.handle(make_decision("threat_detection", "ANOMALOUS"))
        assert result.severity == "WARNING"
        assert result.action == "flag_and_scan"

    def test_spoofed_alert(self):
        result = self.handler.handle(make_decision("threat_detection", "SPOOFED"))
        assert result.alert is True
        assert result.severity == "WARNING"

    def test_confirmed_critical_alert(self):
        result = self.handler.handle(make_decision("threat_detection", "CONFIRMED"))
        assert result.alert is True
        assert result.severity == "CRITICAL"
        assert "escalation" in result.data
        assert result.data["escalation"]["block_recommended"] is True

    def test_resolved_no_alert(self):
        result = self.handler.handle(make_decision("threat_detection", "RESOLVED"))
        assert result.alert is False
        assert result.action == "clear_and_resume"

    def test_result_is_handler_result(self):
        result = self.handler.handle(make_decision("threat_detection", "NOMINAL"))
        assert isinstance(result, HandlerResult)
        assert result.handler == "QUANTA-PULSE"

    def test_to_dict(self):
        result = self.handler.handle(make_decision("threat_detection", "ANOMALOUS"))
        d = result.to_dict()
        assert "handler" in d
        assert "symbol" in d
        assert "action" in d
        assert "timestamp" in d


# ── VigilHandler ──────────────────────────────────────────────────────────────

class TestVigilHandler:
    def setup_method(self):
        self.handler = VigilHandler()

    def test_can_handle_integrity_monitor(self):
        assert self.handler.can_handle("integrity_monitor") is True
        assert self.handler.can_handle("vigil") is True
        assert self.handler.can_handle("threat_detection") is False

    def test_secure_no_alert(self):
        result = self.handler.handle(make_decision("integrity_monitor", "SECURE"))
        assert result.alert is False
        assert result.severity == "INFO"
        assert result.action == "integrity_confirmed"

    def test_degraded_alert(self):
        result = self.handler.handle(make_decision("integrity_monitor", "DEGRADED"))
        assert result.alert is True
        assert result.severity == "WARNING"

    def test_breached_critical_alert(self):
        result = self.handler.handle(make_decision("integrity_monitor", "BREACHED"))
        assert result.alert is True
        assert result.severity == "CRITICAL"
        assert "forensics" in result.data
        assert result.data["forensics"]["isolate_system"] is True

    def test_restoring_recovery_data(self):
        result = self.handler.handle(make_decision("integrity_monitor", "RESTORING"))
        assert "recovery" in result.data
        assert result.data["recovery"]["integrity_rebuild"] is True

    def test_integrity_score_inverted(self):
        # value=0.0 → integrity_score=1.0 (fully secure)
        result = self.handler.handle(make_decision("integrity_monitor", "SECURE", value=0.0))
        assert result.data["integrity_score"] == 1.0


# ── RadHandler ────────────────────────────────────────────────────────────────

class TestRadHandler:
    def setup_method(self):
        self.handler = RadHandler()

    def test_can_handle_rad(self):
        assert self.handler.can_handle("rad") is True
        assert self.handler.can_handle("rf_detection") is True
        assert self.handler.can_handle("threat_detection") is False

    def test_confirmed_signal_response(self):
        d = make_decision("rad", "CONFIRMED")
        d["payload"] = {"frequency": "2.4GHz"}
        result = self.handler.handle(d)
        assert result.alert is True
        assert "signal_response" in result.data
        assert result.data["signal_response"]["log_frequency"] == "2.4GHz"

    def test_nominal_baseline(self):
        result = self.handler.handle(make_decision("rad", "NOMINAL"))
        assert result.action == "baseline_monitor"
        assert result.alert is False


# ── DefaultHandler ────────────────────────────────────────────────────────────

class TestDefaultHandler:
    def setup_method(self):
        self.handler = DefaultHandler()

    def test_can_handle_anything(self):
        assert self.handler.can_handle("unknown_grammar") is True
        assert self.handler.can_handle("") is True

    def test_handle_unrecognized(self):
        d = make_decision("mystery_grammar", "SOME_STATE")
        result = self.handler.handle(d)
        assert result.handler == "DEFAULT"
        assert result.action == "log_unrouted_decision"
        assert result.alert is False
        assert result.data["grammar"] == "mystery_grammar"
