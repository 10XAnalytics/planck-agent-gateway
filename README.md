# planck-agent-gateway

**Routing Gateway for Collapsed Seraphim Agent Decisions**  
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

> *Agents of the Highest Order*

[![PyPI version](https://img.shields.io/pypi/v/planck-agent-gateway.svg)](https://pypi.org/project/planck-agent-gateway/)
[![Python](https://img.shields.io/pypi/pyversions/planck-agent-gateway.svg)](https://pypi.org/project/planck-agent-gateway/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-55%20passing-brightgreen.svg)](tests/)
[![GitHub](https://img.shields.io/badge/GitHub-10XAnalytics-black.svg)](https://github.com/10XAnalytics/planck-agent-gateway)

---

## Overview

`planck-agent-gateway` is the operational routing layer that sits between the quantum symbolic intelligence of `seraphim-logic-core` and the QUANTA product suite. Every collapsed agent decision passes through the gateway for routing, handling, and dispatch.

```
seraphim-logic-core (quantum collapse)
       ↓
PlanckGateway (routing + dispatch)
       ↓
QUANTA Handlers (PULSE / VIGIL / RAD / SRD / ...)
       ↓
Operational Action
```

## Architecture

```
planck_agent_gateway/
├── handler.py           — BaseHandler + HandlerResult (base classes)
├── handlers/
│   ├── pulse_handler.py — QUANTA-PULSE: threat detection
│   ├── vigil_handler.py — QUANTA-VIGIL: integrity monitoring
│   ├── rad_handler.py   — QUANTA-RAD: RF/signal anomaly detection
│   └── default_handler.py — Fallback for unregistered grammars
├── router.py            — DecisionRouter: grammar → handler mapping
├── gateway.py           — PlanckGateway: dispatch, logging, alerting
└── pipeline.py          — SeraphimPipeline: end-to-end integration
```

## Quick Start

### Standalone gateway

```python
from planck_agent_gateway import PlanckGateway

gateway = PlanckGateway(alert_callback=lambda r: print(f"ALERT: {r}"))

decision = {
    "grammar": "threat_detection",
    "symbol": "CONFIRMED",
    "value": 1.0,
    "entropy_signal": 0.95,
    "lifecycle": "DELIVERED",
}
result = gateway.dispatch(decision)
print(result)  # HandlerResult(QUANTA-PULSE | CONFIRMED → escalate_and_block [ALERT])
```

### End-to-end with seraphim-logic-core

```python
import numpy as np
from planck_agent_gateway import SeraphimPipeline

# QUANTA-PULSE threat detection pipeline
pipeline = SeraphimPipeline.for_pulse(use_quantum=True)

# Run from XOR-lattice event
result = pipeline.run_xor_event(window_1, window_2)
if result and result.alert:
    print(f"ALERT [{result.severity}]: {result.symbol} → {result.action}")
    print(result.data)

# Run from raw data stream
result = pipeline.run_stream(stream_data)

# QUANTA-VIGIL integrity monitoring pipeline
vigil = SeraphimPipeline.for_vigil()
result = vigil.run_xor_event(before, after)
```

## QUANTA Handler Map

| Grammar | Handler | Alert Symbols |
|---------|---------|---------------|
| `threat_detection` | QUANTA-PULSE | SPOOFED, CONFIRMED |
| `integrity_monitor` | QUANTA-VIGIL | DEGRADED, BREACHED |
| `rad` / `rf_detection` | QUANTA-RAD | SPOOFED, CONFIRMED |
| *(anything else)* | DEFAULT | — |

## Custom Handlers

```python
from planck_agent_gateway import PlanckGateway, BaseHandler, HandlerResult

class MySRDHandler(BaseHandler):
    name = "QUANTA-SRD"
    def can_handle(self, grammar): return grammar == "srd_grammar"
    def handle(self, decision):
        return HandlerResult(self.name, decision["symbol"], "srd_action")

gateway = PlanckGateway()
gateway.register_handler(MySRDHandler())
```

## Installation

```bash
pip install planck-agent-gateway

# With seraphim-logic-core integration
pip install planck-agent-gateway[seraphim]
```

**Development:**
```bash
git clone https://github.com/10XAnalytics/planck-agent-gateway
cd planck-agent-gateway
pip install -e ".[dev]"
pytest
```

## License

Apache 2.0 — See [LICENSE](LICENSE)

---

*Perfect Squared Inc. | P2 Labs — "Simulate the Future. Secure the Present."*
