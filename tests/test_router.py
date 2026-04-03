"""Tests for the DecisionRouter."""

import pytest
from planck_agent_gateway.router import DecisionRouter
from planck_agent_gateway.handler import HandlerResult


def make_decision(grammar, symbol):
    return {
        "agent_id": "TEST-001",
        "grammar": grammar,
        "symbol": symbol,
        "value": 0.5,
        "entropy_cost": 0.3,
        "information_gain": 0.7,
        "entropy_signal": 0.6,
        "lifecycle": "DELIVERED",
    }


class TestDecisionRouter:
    def setup_method(self):
        self.router = DecisionRouter()

    def test_routes_threat_detection_to_pulse(self):
        decision = make_decision("threat_detection", "ANOMALOUS")
        result = self.router.route(decision)
        assert result.handler == "QUANTA-PULSE"

    def test_routes_integrity_monitor_to_vigil(self):
        decision = make_decision("integrity_monitor", "BREACHED")
        result = self.router.route(decision)
        assert result.handler == "QUANTA-VIGIL"

    def test_routes_rad_to_rad(self):
        decision = make_decision("rad", "CONFIRMED")
        result = self.router.route(decision)
        assert result.handler == "QUANTA-RAD"

    def test_routes_unknown_to_default(self):
        decision = make_decision("unknown_grammar", "SOME_STATE")
        result = self.router.route(decision)
        assert result.handler == "DEFAULT"

    def test_resolve_returns_correct_handler(self):
        handler = self.router.resolve("threat_detection")
        assert handler.name == "QUANTA-PULSE"

    def test_resolve_fallback_to_default(self):
        handler = self.router.resolve("not_registered")
        assert handler.name == "DEFAULT"

    def test_registered_handlers_list(self):
        names = self.router.registered_handlers()
        assert "QUANTA-PULSE" in names
        assert "QUANTA-VIGIL" in names
        assert "QUANTA-RAD" in names

    def test_register_custom_handler(self):
        from planck_agent_gateway.handler import BaseHandler, HandlerResult

        class MyHandler(BaseHandler):
            name = "MY-HANDLER"
            def can_handle(self, grammar): return grammar == "custom"
            def handle(self, decision): return HandlerResult(self.name, "X", "custom_action")

        self.router.register(MyHandler())
        decision = make_decision("custom", "X")
        result = self.router.route(decision)
        assert result.handler == "MY-HANDLER"

    def test_route_returns_handler_result(self):
        decision = make_decision("threat_detection", "NOMINAL")
        result = self.router.route(decision)
        assert isinstance(result, HandlerResult)

    def test_repr(self):
        r = repr(self.router)
        assert "DecisionRouter" in r
        assert "QUANTA-PULSE" in r
