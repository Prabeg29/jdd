"""``settings.anthropic``: Anthropic credentials. Model options live in pipeline.yaml."""

from pydantic import SecretStr

from shared.schemas.base import StrictModel


class AnthropicSettings(StrictModel):
    api_key: SecretStr
