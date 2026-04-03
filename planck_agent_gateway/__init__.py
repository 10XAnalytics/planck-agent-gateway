"""
planck-agent-gateway
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

Gateway layer that routes collapsed Seraphim agent decisions
into QUANTA operational product handlers.

    seraphim-logic-core → planck-agent-gateway → QUANTA
"""

__version__ = "0.1.0"
__author__ = "Perfect Squared Inc. | P2 Labs"
__license__ = "Apache-2.0"

from .handler import BaseHandler, HandlerResult
from .handlers import PulseHandler, VigilHandler, RadHandler, DefaultHandler
from .router import DecisionRouter
from .gateway import PlanckGateway
from .pipeline import SeraphimPipeline

__all__ = [
    # Handler base
    "BaseHandler",
    "HandlerResult",
    # Handlers
    "PulseHandler",
    "VigilHandler",
    "RadHandler",
    "DefaultHandler",
    # Routing
    "DecisionRouter",
    # Gateway
    "PlanckGateway",
    # Pipeline
    "SeraphimPipeline",
]
