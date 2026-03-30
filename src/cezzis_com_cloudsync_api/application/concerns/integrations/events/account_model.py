"""Account model for integration events."""

from cezzis_com_cloudsync_api.application.concerns.integrations.events.account_address_model import AccountAddressModel
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class AccountModel(BaseModel):
    """Account information within integration events."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: str | None = None
    subject_id: str
    given_name: str | None = None
    family_name: str | None = None
    display_name: str | None = None
    email: str | None = None
    primary_address: AccountAddressModel | None = None
