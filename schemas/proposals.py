# ============================================================================
# JOB PROPOSAL SCHEMA
# ============================================================================

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
import time

from schemas.imports import ProposalState, JobTimeline, PriceBreakDown, ObjectId


class JobProposalBase(BaseModel):
    job_id: str
    agent_id: str
    proposal: str
    break_down: Optional[PriceBreakDown] = None
    timeline: Optional[JobTimeline] = None
    status: ProposalState = Field(default=ProposalState.pending_review)
    proposal_created_by_user_id: Optional[str] = None
    proposal_created_by_role: Optional[str] = None
    proposal_created_via: Optional[str] = None
    date_created: int = Field(default_factory=lambda: int(time.time()))
    last_updated: int = Field(default_factory=lambda: int(time.time()))
    model_config = ConfigDict(extra="forbid")


class JobProposalCreate(JobProposalBase):
    model_config = ConfigDict(extra="forbid")


class JobProposalUpdate(BaseModel):
    proposal: Optional[str] = None
    break_down: Optional[PriceBreakDown] = None
    timeline: Optional[JobTimeline] = None
    status: Optional[ProposalState] = None
    proposal_created_by_user_id: Optional[str] = None
    proposal_created_by_role: Optional[str] = None
    proposal_created_via: Optional[str] = None
    last_updated: int = Field(default_factory=lambda: int(time.time()))
    model_config = ConfigDict(extra="forbid")


class JobProposalOut(JobProposalBase):
    id: Optional[str] = None

    @model_validator(mode="before")
    def set_dynamic_values(cls, values):  # type: ignore
        values["id"] = str(values.get("_id"))
        return values

    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
