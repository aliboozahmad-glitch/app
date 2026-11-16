from datetime import UTC, datetime
from typing import Annotated, Literal

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from .genetics.mendelian import MODES

PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]
Lang = Literal["en", "ar", "de"]
Short = Annotated[str, Field(min_length=1, max_length=6)]
Region = Literal["gulf", "middle_east_north_africa", "europe", "sub_saharan_africa", "south_asia", "east_asia",
                 "americas", "global"]


class BaseDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: PyObjectId | None = Field(default=None, alias="_id")

    @classmethod
    def from_mongo(cls, doc: dict):
        return cls.model_validate(doc)

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data


class AnalysisDoc(BaseDocument):
    user_id: str
    analysis_type: str
    request: dict
    result: dict
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MendelianIn(Strict):
    mode: Literal[MODES]  # type: ignore[valid-type]
    parent1: Short
    parent2: Short


class BloodTypeIn(Strict):
    parent1_abo: Annotated[str, Field(min_length=1, max_length=2)]
    parent1_rh: Annotated[str, Field(min_length=1, max_length=2)]
    parent2_abo: Annotated[str, Field(min_length=1, max_length=2)]
    parent2_rh: Annotated[str, Field(min_length=1, max_length=2)]


class CarrierIn(Strict):
    disease_id: Annotated[str, Field(min_length=1, max_length=40)]
    mother_status: Literal["affected", "carrier", "non_carrier", "unknown"]
    father_status: Literal["affected", "carrier", "non_carrier", "unaffected", "unknown"]
    region: Region | None = None


class HeightIn(Strict):
    mother_cm: float = Field(ge=120, le=230)
    father_cm: float = Field(ge=120, le=230)


class PigmentIn(Strict):
    trait: Literal["eye_color", "hair_color"]
    mother: Annotated[str, Field(min_length=1, max_length=10)]
    father: Annotated[str, Field(min_length=1, max_length=10)]


Gender = Literal["male", "female"]


class FamilyPatternIn(Strict):
    wife: Annotated[list[Gender], Field(min_length=1, max_length=3)]
    husband: Annotated[list[Gender], Field(min_length=1, max_length=3)]
    child_number: Literal[1, 2] = 1


class SexRatioIn(Strict):
    pass


class RoleIn(Strict):
    role: str
