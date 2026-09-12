from pydantic import BaseModel


class VersionRs(BaseModel):
    """Version response model."""

    version: str
