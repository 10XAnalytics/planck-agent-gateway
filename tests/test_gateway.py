"""Tests for the PlanckGateway."""

import pytest
from planck_agent_gateway.gateway import PlanckGateway
from planck_agent_gateway.handler import HandlerResult


def make_decision(grammar, symbol, entropy=0.7):
    return {
        "agent_id": "TEST-001",
        "grammar": grammar,
        "symbol": symbol,
        "value": 0.5,
        "entropy_cost": 0.3,
        "information_gain": 0.7,
        "entropy_signal": entropy,
        "lifecycle": "DELIVERED",
        "swarm_size": 4,
    }


class TestPlanckGateway:
    def setup_method(self):
        self.gateway = PlanckGateway()

    def test_dispatch_returns_result(self):
        d = make_decision("threat_detection", "NOMINAL")
        result = self.gateway.dispatch(d)
        assert isinstance(result, HandlerResult)

    def test_dispatch_increments_stats(self):
        d = make_decision("threat_detection", "NOMINAL")
        self.gateway.dispatch(d)
        assert self.gateway.stats()["total_decisions"] == 1

    def test_dispatch_alert_increments_alert_count(self):
        d = make_decision("threat_detection", "CONFIRMED")
        self.gateway.dispatch(d)
        assert self.gateway.stats()["total_alerts"] == 1

    def test_dispatch_non_alert_no_alert_count(self):
        d = make_decision("threat_detection", "NOMINAL")
        self.gateway.dispatch(d)
        assert self.gateway.stats()["total_alerts"] == 0

    def test_alert_callback_fired(self):
        fired = []
        gw = PlanckGateway(alert_callback=lambda r: fired.append(r))
        d = make_decision("threat_detection", "CONFIRMED")
        gw.dispatch(d)
        assert len(fired) == 1
        assert fired[0].alert is True

    def test_alert_callback_not_fired_for_non_alert(self):
        fired = []
        gw = PlanckGateway(alert_callback=lambda r: fired.append(r))
        d = make_decision("threat_detection", "NOMINAL")
        gw.dispatch(d)
        assert len(fired) == 0

    def test_dispatch_many(self):
        decisions = [
            make_decision("threat_detection", "NOMINAL"),
            make_decision("integrity_monitor", "SECURE"),
            make_decision("threat_detection", "ANOMALOUS"),
        ]
        results = self.gateway.dispatch_many(decisions)
        assert len(results) == 3
        assert self.gateway.stats()["total_decisions"] == 3

    def test_dispatch_swarm_verdict(self):
        verdict = {**make_decision("threat_detection", "SPOOFED"), "swarm_votes": {"SPOOFED": 2.1}}
        result = self.gateway.dispatch_swarm_verdict(verdict)
        assert result.handler == "QUANTA-PULSE"
        assert result.alert is True

    def test_recent_returns_last_n(self):
        for sym in ["NOMINAL", "ANOMALOUS", "RESOLVED"]:
            self.gateway.dispatch(make_decision("threat_detection", sym))
        recent = self.gateway.recent(2)
        assert len(recent) == 2

    def test_alerts_filter(self):
        self.gateway.dispatch(make_decision("threat_detection", "NOMINAL"))
        self.gateway.dispatch(make_decision("threat_detection", "CONFIRMED"))
        alerts = self.gateway.alerts()
        assert len(alerts) == 1
        assert alerts[0]["symbol"] == "CONFIRMED"

    def test_stats_by_handler(self):
        self.gateway.dispatch(make_decision("threat_detection", "NOMINAL"))
        self.gateway.dispatch(make_decision("integrity_monitor", "SECURE"))
        stats = self.gateway.stats()
        assert stats["by_handler"]["QUANTA-PULSE"] == 1
        assert stats["by_handler"]["QUANTA-VIGIL"] == 1

    def test_stats_by_symbol(self):
        self.gateway.dispatch(make_decision("threat_detection", "ANOMALOUS"))
        self.gateway.dispatch(make_decision("threat_detection", "ANOMALOUS"))
        stats = self.gateway.stats()
        assert stats["by_symbol"]["ANOMALOUS"] == 2

    def test_reset_stats(self):
        self.gateway.dispatch(make_decision("threat_detection", "NOMINAL"))
        self.gateway.reset_stats()
        assert self.gateway.stats()["total_decisions"] == 0

    def test_reset_log(self):
        self.gateway.dispatch(make_decision("threat_detection", "NOMINAL"))
        self.gateway.reset_log()
        assert self.gateway.recent() == []

    def test_repr(self):
        r = repr(self.gateway)
        assert "PlanckGateway" in r

    def test_log_bounded(self):
        gw = PlanckGateway(log_size=5)
        for _ in range(10):
            gw.dispatch(make_decision("threat_detection", "NOMINAL"))
        assert len(gw.recent(100)) == 5
