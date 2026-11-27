"""``settings.aws``: AWS resource names, set by Terraform as ``AWS__*`` variables."""

from shared.schemas.base import StrictModel


class AwsSettings(StrictModel):
    region: str = "ap-southeast-2"
    bucket: str
    ingest_queue_url: str | None = None
    ingest_dlq_url: str | None = None
