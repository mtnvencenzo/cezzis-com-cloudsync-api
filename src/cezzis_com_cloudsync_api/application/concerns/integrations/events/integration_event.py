"""Base interface for integration events."""

from abc import ABC

from pydantic import BaseModel


class IIntegrationEvent(BaseModel, ABC):
    """Base class for all integration events received from Dapr."""
