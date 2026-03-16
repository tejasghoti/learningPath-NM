# app/schemas/student_schema.py
from pydantic import BaseModel, field_validator
from typing import Literal

class StudentCreate(BaseModel):
    caste: Literal["SC","ST","OBC","GEN"]
    income: int
    state: str
    gender: Literal["MALE","FEMALE"]
    course: str

    @field_validator("income")
    @classmethod
    def income_positive(cls, v):
        if v <= 0:
            raise ValueError("Income must be positive")
        return v

    @field_validator("state")
    @classmethod
    def normalize_state(cls, v):
        return v.upper()
