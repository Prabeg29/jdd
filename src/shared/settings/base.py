"""``settings``: every runtime setting, grouped, e.g. ``settings.database.host``.

Import the instance, never build another: ``from shared.settings.base import settings``.

Where values come from, highest priority first:

1. Environment variables, with ``__`` between levels: ``DATABASE__HOST``, ``AWS__BUCKET``.
2. A ``.env`` file in the working directory (local development).
3. SSM Parameter Store, only when ``SSM_PARAMETERS_PATH`` is set (Lambda). Each
   parameter under that path is one field, with ``/`` between levels:
   ``/job-discovery/database/password`` sets ``settings.database.password``.
"""

import os

from pydantic_settings import (
    AWSSystemsManagerSettingsSource,
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from shared.settings.anthropic import AnthropicSettings
from shared.settings.aws import AwsSettings
from shared.settings.database import DatabaseSettings
from shared.settings.logging import LogSettings
from shared.settings.slack import SlackSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
        # .env and the environment hold unrelated variables too.
        extra="ignore",
        frozen=True,
    )

    aws: AwsSettings
    database: DatabaseSettings
    anthropic: AnthropicSettings
    slack: SlackSettings
    log: LogSettings = LogSettings()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources = [init_settings, env_settings, dotenv_settings]
        ssm_path = os.environ.get("SSM_PARAMETERS_PATH")
        if ssm_path:
            sources.append(
                AWSSystemsManagerSettingsSource(
                    settings_cls,
                    ssm_path=ssm_path,
                    case_sensitive=False,
                )
            )
        return tuple(sources)


# The one instance, loaded once per process (once per Lambda container).
settings = Settings()
