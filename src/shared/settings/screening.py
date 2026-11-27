"""``screening.yaml``: the screening rules, kept only in the private S3 bucket."""

from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator

from shared.schemas.base import StrictModel
from shared.utils.yaml_input import content_hash

Phrase = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
CountryCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]
CurrencyCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
UnknownPolicy = Literal["keep", "fail"]


class TitleRules(StrictModel):
    allow: list[Phrase] = Field(min_length=1)
    avoid: list[Phrase] = []
    abbreviations: dict[Phrase, Phrase] = {}


class AcceptedPlace(StrictModel):
    """A country, optionally narrowed to a region and/or a city."""

    country: CountryCode
    region: Phrase | None = None
    city: Phrase | None = None


class LocationRules(StrictModel):
    accept: list[AcceptedPlace] = []
    accept_remote: list[CountryCode] = []
    unknown: UnknownPolicy = "keep"


class CandidateWorkRights(StrictModel):
    status: Phrase
    needs_sponsorship: bool


class WorkRightsRules(StrictModel):
    """Decided by the judge; there is deliberately no ``unknown`` policy."""

    candidate: CandidateWorkRights


class SalaryRules(StrictModel):
    currency: CurrencyCode
    min_annual: int = Field(gt=0)
    unknown: UnknownPolicy = "keep"


class ExperienceRules(StrictModel):
    """Decided by the judge; there is deliberately no ``unknown`` policy."""

    candidate_years: float = Field(ge=0)
    tolerance: float = Field(ge=0)


class TitleChecks(StrictModel):
    """Titles the operator expects to pass or fail the title rule."""

    pass_: list[Phrase] = Field(default=[], alias="pass")
    fail: list[Phrase] = []

    model_config = StrictModel.model_config | {"populate_by_name": True}


class ScreeningRules(StrictModel):
    title: TitleRules
    location: LocationRules | None = None
    work_rights: WorkRightsRules | None = None
    salary: SalaryRules | None = None
    experience: ExperienceRules | None = None
    blocked_companies: list[Phrase] = []
    checks: TitleChecks = TitleChecks()

    @field_validator("blocked_companies")
    @classmethod
    def _unique_blocked(cls, value: list[str]) -> list[str]:
        if len({v.casefold() for v in value}) != len(value):
            raise ValueError("duplicate company")
        return value

    @property
    def ruleset_version(self) -> str:
        """SHA-256 of the parsed rules as canonical JSON, excluding ``checks``."""
        return content_hash(self.model_dump(mode="json", exclude={"checks"}))
