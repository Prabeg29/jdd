"""``settings.slack``: Slack credentials. Channel and posting options live in pipeline.yaml."""

from pydantic import SecretStr

from shared.schemas.base import StrictModel


class SlackSettings(StrictModel):
    bot_token: SecretStr
