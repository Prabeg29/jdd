import json
import logging
from typing import Any

import boto3
from sqlalchemy import select

from shared.models import Company
from shared.settings.base import settings
from shared.settings.screening import ScreeningRules
from shared.utils.session import SessionLocal
from shared.utils.yaml_input import InvalidInput, parse_yaml

s3_client = boto3.client("s3", region_name=settings.aws.region)
sqs_client = boto3.client("sqs", region_name=settings.aws.region)

# Lambda formats log records as JSON (log_format = "JSON" in infra/lambda.tf)
logger = logging.getLogger()
logger.setLevel("INFO")

BATCH_SIZE = 10


def send_companies_to_sqs(queue_url: str, screening_criteria: ScreeningRules) -> int:
    """Read companies in chunks and push one SQS message per company"""
    criteria = screening_criteria.model_dump(mode="json")
    sent = 0

    with SessionLocal() as session:
        companies = session.scalars(
            select(Company)
            .where(Company.enabled)
            .order_by(Company.id)
            .execution_options(yield_per=BATCH_SIZE)
        )
        for chunk in companies.partitions():
            entries = [
                {
                    "Id": str(company.id),
                    "MessageBody": json.dumps(
                        {
                            "company_id": company.id,
                            "ats": company.ats,
                            "board_token": company.board_token,
                            "screening_criteria": criteria,
                        }
                    ),
                }
                for company in chunk
            ]
            response = sqs_client.send_message_batch(QueueUrl=queue_url, Entries=entries)
            if response.get("Failed"):
                raise RuntimeError(f"{len(response['Failed'])} SQS messages failed to send")
            sent += len(entries)

    return sent


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    try:
        response = s3_client.get_object(Bucket=settings.aws.bucket, Key="screening.yaml")
        screening_criteria = parse_yaml(ScreeningRules, response["Body"].read())
        sent = send_companies_to_sqs(settings.aws.ingest_queue_url, screening_criteria)
    except InvalidInput as e:
        logger.error("Failed to load screening criteria", extra={"error": type(e).__name__})
        return {"statusCode": 400, "message": "Invalid screening criteria"}
    except Exception as e:
        logger.error("Error dispatching companies", extra={"error": type(e).__name__})
        raise

    logger.info("Dispatched companies", extra={"companies": sent})
    return {"statusCode": 200, "message": f"Dispatched {sent} companies"}
