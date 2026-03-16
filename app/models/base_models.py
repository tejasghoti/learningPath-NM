# app/models/base_models.py
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator


# ─── Scholarship Table ───
class Scholarship(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    provider_name: str

    # Relationship: One Scholarship has MANY EligibilityCriteria
    criteria: List["EligibilityCriteria"] = Relationship(back_populates="scholarship")


# ─── EligibilityCriteria Table ───
class EligibilityCriteria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # FOREIGN KEY: Links this criteria row back to a specific scholarship
    scholarship_id: int = Field(foreign_key="scholarship.id")
    
    # The actual eligibility rules
    target_caste: str = Field(index=True)
    max_income_limit: int
    target_state: str
    target_gender: str = "ALL"
    target_course: str = "ALL"

    # Relationship back to the parent Scholarship
    scholarship: Optional[Scholarship] = Relationship(back_populates="criteria")


# ─── Student Table ───
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    caste: str = Field(index=True)
    income: int
    state: str = Field(index=True)
    gender: str
    course: str

    @field_validator("income")
    @classmethod
    def income_positive(cls, v):
        if v < 0:
            raise ValueError("Income must be positive")
        return v

    @field_validator("state")
    @classmethod
    def normalize_state(cls, v):
        return v.upper()
