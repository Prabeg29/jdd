# job-discovery

## Lambda function style

Every service lives in `src/<service>/main.py`, and Lambda calls `handler` (`<service>.main.handler`).
Write these files in the flat style of the AWS docs examples. `src/sync_watchlist/main.py`
is the reference: when in doubt, copy its shape.

### Layout, top to bottom

1. Imports.
2. Module-level setup, which runs once per container:
   - SDK clients: `s3_client = boto3.client("s3", region_name=settings.aws.region)`
   - Database sessions: `from shared.utils.session import SessionLocal`
   - Logger: `logger = logging.getLogger()` then `logger.setLevel("INFO")`
   - Constants: `BATCH_SIZE = 10`, with a comment if the value is a limit set by AWS.
3. One or two plain helper functions that do the real work, each with a one-line docstring.
4. `handler(event, context)` at the bottom.

### Rules

- **Settings:** read them only through `from shared.settings.base import settings`, which
  groups them (e.g. `settings.aws.bucket`, `settings.database.host`). Never read
  `os.environ` and never construct another `Settings()`.
- **Logging:** use the root logger and pass fields with `extra={...}`. Lambda formats the
  output as JSON (`log_format = "JSON"` in `infra/lambda.tf`), so there's no custom
  logging setup.
- **Handler body:** one `try` around the whole flow.
  - Catch the expected bad-input error first (e.g. `InvalidInput`). Log it and return
    `{"statusCode": 400, "message": ...}`.
  - Then catch `Exception`, log `extra={"error": type(e).__name__}`, and re-raise so
    Lambda records the failure.
  - On success, log a summary and return `{"statusCode": 200, "message": ...}`.
- **Inlining:** a step of one to three lines goes straight into the handler, not into its
  own function.
- **Type hints:** type every function signature. The handler is
  `def handler(event: dict[str, Any], context: Any) -> dict[str, Any]`.
- **Code to leave out unless asked:**
  - event validation or idempotency markers
  - custom metrics (CloudWatch's built-in Lambda metrics are enough)
  - a separate `core.py`
  - runtime or container dataclasses
  - dependency-injection parameters

### Skeleton

```python
import logging
from typing import Any

import boto3

from shared.settings.base import settings
from shared.utils.session import SessionLocal

s3_client = boto3.client("s3", region_name=settings.aws.region)

# Lambda formats log records as JSON (log_format = "JSON" in infra/lambda.tf)
logger = logging.getLogger()
logger.setLevel("INFO")


def do_work(...) -> int:
    """One line on what this does"""
    with SessionLocal() as session:
        ...


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    try:
        ...
        count = do_work(...)
    except InvalidInput as e:
        logger.error("Invalid input", extra={"error": type(e).__name__})
        return {"statusCode": 400, "message": "Invalid input"}
    except Exception as e:
        logger.error("Error doing work", extra={"error": type(e).__name__})
        raise

    logger.info("Did work", extra={"count": count})
    return {"statusCode": 200, "message": f"Processed {count}"}
```
