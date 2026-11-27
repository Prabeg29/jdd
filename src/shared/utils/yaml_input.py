"""Parse YAML documents into Pydantic models, reporting problems by field path only.

Pydantic error messages can echo the offending input, and these files hold personal
data, so a problem is reported as ``<path>: <error type>`` and nothing else.
"""

import hashlib
import json
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError


class InvalidInput(Exception):
    """A YAML document that is malformed or does not match its schema."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        super().__init__("; ".join(problems))


def field_paths(error: ValidationError) -> list[str]:
    """``path: type`` for each error, never the input value or Pydantic's message."""
    problems = []
    for item in error.errors(include_input=False, include_url=False):
        path = ".".join(str(part) for part in item["loc"]) or "<root>"
        if item["type"] == "value_error":
            # Raised by this project's validators, whose messages never quote values.
            problems.append(f"{path}: {item['msg'].removeprefix('Value error, ')}")
        else:
            problems.append(f"{path}: {item['type']}")
    return problems


def parse_yaml[T: BaseModel](model: type[T], text: str | bytes) -> T:
    """Parse ``text`` as YAML and validate it against ``model``."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}" if mark is not None else ""
        raise InvalidInput([f"<yaml>: malformed{where}"]) from None
    if data is None:
        data = {}
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise InvalidInput(field_paths(exc)) from None


def canonical_json(data: Any) -> str:
    """Key-sorted, whitespace-free JSON used for content hashes."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode()).hexdigest()
