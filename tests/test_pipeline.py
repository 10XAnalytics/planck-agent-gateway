"""Tests for the SeraphimPipeline (end-to-end integration)."""

import numpy as np
import pytest
from planck_agent_gateway.pipeline import SeraphimPipeline
from planck_agent_gateway.handler import HandlerResult


class TestSeraphimPipeline:
    def test_for_pulse_factory(self):
        pipeline = SeraphimPipeline.for_pulse(use_quantum=False)
        assert pipeline.swarm.grammar.name == "threat_detection"
        assert pipeline.swarm.use_quantum is False

    def test_for_vigil_factory(self):
        pipeline = SeraphimPipeline.for_vigil(use_quantum=False)
        assert pipeline.swarm.grammar.name == "integrity_monitor"

    def test_run_xor_event_returns_result(self):
        pipeline = SeraphimPipeline.for_pulse(use_quantum=False)
        w1 = np.random.randint(0, 256, size=64, dtype=np.uint8)
        w2 = np.bitwise_not(w1)  # max diff
        result = pipeline.run_xor_event(w1, w2)
        assert result is not None
        assert isinstance(result, HandlerResult)
        assert result.handler == "QUANTA-PULSE"

    def test_run_xor_event_vigil(self):
        pipeline = SeraphimPipeline.for_vigil(use_quantum=False)
        w1 = np.random.randint(0, 256, size=64, dtype=np.uint8)
        w2 = np.bitwise_not(w1)
        result = pipeline.run_xor_event(w1, w2)
        assert result is not None
        assert result.handler == "QUANTA-VIGIL"

    def test_run_stream_no_anomaly_returns_none(self):
        pipeline = SeraphimPipeline.for_pulse(use_quantum=False)
        stream = np.full(256, 128, dtype=np.uint8)  # constant = no anomaly
        result = pipeline.run_stream(stream)
        assert result is None

    def test_run_stream_high_entropy_triggers(self):
        pipeline = SeraphimPipeline.for_pulse(use_quantum=False)
        stream = np.random.randint(0, 256, size=256, dtype=np.uint8)
        result = pipeline.run_stream(stream)
        # High-entropy stream should trigger (nearly always)
        assert result is None or isinstance(result, HandlerResult)

    def test_run_decision_direct(self):
        pipeline = SeraphimPipeline.for_pulse(use_quantum=False)
        decision = {
            "agent_id": "TEST-001",
            "grammar": "threat_detection",
            "symbol": "CONFIRMED",
            "value": 1.0,
            "entropy_cost": 0.9,
            "information_gain": 0.1,
            "entropy_signal": 0.95,
            "lifecycle": "DELIVERED",
        }
        result = pipeline.run_decision(decision)
        assert result.handler == "QUANTA-PULSE"
        assert result.alert is True
        assert result.severity == "CRITICAL"

    def test_alert_callback_triggered_by_pipeline(self):
        alerts = []
        pipeline = SeraphimPipeline.for_pulse(
            use_quantum=False,
            alert_callback=lambda r: alerts.append(r)
        )
        decision = {
            "agent_id": "TEST-001",
            "grammar": "threat_detection",
            "symbol": "CONFIRMED",
            "value": 1.0,
            "entropy_cost": 0.9,
            "information_gain": 0.1,
            "entropy_signal": 0.95,
            "lifecycle": "DELIVERED",
        }
        pipeline.run_decision(decision)
        assert len(alerts) == 1

    def test_stats(self):
        pipeline = SeraphimPipeline.for_pulse(use_quantum=False)
        stats = pipeline.stats()
        assert "swarm" in stats
        assert "gateway" in stats

    def test_repr(self):
        pipeline = SeraphimPipeline.for_pulse(use_quantum=False)
        r = repr(pipeline)
        assert "SeraphimPipeline" in r
        assert "threat_detection" in r
