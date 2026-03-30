"""Account address model for integration events."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class AccountAddressModel(BaseModel):
    """Address information for an account."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    address_line1: str | None = None
    city: str | None = None
    region: str | None = None
    postal_code: str | None = None
    country: str | None = None
