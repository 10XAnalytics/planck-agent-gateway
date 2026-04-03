"""
planck-agent-gateway — Base Handler
Perfect Squared Inc. | P2 Labs | Seraphim |LZ⟩

All QUANTA product handlers inherit from BaseHandler.
A handler receives a collapsed agent decision dict and performs
the appropriate operational action for its product domain.

Decision dict schema (from seraphim-logic-core):
    {
        "agent_id":        str,
        "grammar":         str,    # e.g. "threat_detection", "integrity_monitor"
        "symbol":          str,    # e.g. "ANOMALOUS", "BREACHED"
        "value":           float,
        "entropy_cost":    float,
        "information_gain": float,
        "entropy_signal":  float,
        "lifecycle":       str,    # "DELIVERED"
        "payload":         dict,   # optional — domain-specific data
        "swarm_size":      int,    # optional — if from a swarm
        "swarm_votes":     dict,   # optional
    }
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import time


class HandlerResult:
    """Standardized result returned by every handler."""

    def __init__(
        self,
        handler: str,
        symbol: str,
        action: str,
        data: Optional[dict] = None,
        alert: bool = False,
        severity: str = "INFO",
    ):
        self.handler = handler
        self.symbol = symbol
        self.action = action
        self.data = data or {}
        self.alert = alert
        self.severity = severity          # INFO | WARNING | CRITICAL
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "handler":   self.handler,
            "symbol":    self.symbol,
            "action":    self.action,
            "data":      self.data,
            "alert":     self.alert,
            "severity":  self.severity,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        flag = " [ALERT]" if self.alert else ""
        return f"HandlerResult({self.handler} | {self.symbol} → {self.action}{flag})"


class BaseHandler(ABC):
    """
    Abstract base class for all QUANTA product handlers.

    Subclass this and implement `handle()` for each QUANTA product
    (PULSE, RAD, VIGIL, SRD, etc.).
    """

    name: str = "base"

    @abstractmethod
    def handle(self, decision: dict) -> HandlerResult:
        """
        Process a collapsed agent decision.

        Args:
            decision: Collapsed state dict from seraphim-logic-core

        Returns:
            HandlerResult with action taken, severity, and optional alert flag
        """

    def can_handle(self, grammar: str) -> bool:
        """Return True if this handler can process decisions from the given grammar."""
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
