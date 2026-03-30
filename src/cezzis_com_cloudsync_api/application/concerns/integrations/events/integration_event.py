"""Base interface for integration events."""

from abc import ABC
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class IIntegrationEvent(BaseModel, ABC):
    """Base class for all integration events received from Dapr."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    id: str = Field(default_factory=lambda: str(uuid4()))
    creation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
