"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional


class CustomerInput(BaseModel):
    """Input schema for a single customer prediction."""

    # Demographics
    Adult_Dependents: int = Field(default=0, ge=0, le=10)
    Child_Dependents: int = Field(default=0, ge=0, le=10)
    Infant_Dependents: int = Field(default=0, ge=0, le=5)
    Estimated_Annual_Income: float = Field(default=50000, ge=0)
    Employment_Status: str = Field(default="Employed")
    Region_Code: int = Field(default=1, ge=1)

    # History & Risk
    Existing_Policyholder: str = Field(default="No")
    Previous_Claims_Filed: int = Field(default=0, ge=0)
    Years_Without_Claims: int = Field(default=0, ge=0)
    Previous_Policy_Duration_Months: int = Field(default=0, ge=0)
    Policy_Cancelled_Post_Purchase: str = Field(default="No")

    # Policy Details
    Deductible_Tier: int = Field(default=3, ge=1, le=5)
    Payment_Schedule: str = Field(default="Monthly")
    Vehicles_on_Policy: int = Field(default=1, ge=0)
    Custom_Riders_Requested: int = Field(default=0, ge=0)
    Grace_Period_Extensions: int = Field(default=0, ge=0)

    # Sales & Underwriting
    Days_Since_Quote: int = Field(default=7, ge=0)
    Underwriting_Processing_Days: int = Field(default=5, ge=0)
    Policy_Amendments_Count: int = Field(default=0, ge=0)
    Acquisition_Channel: str = Field(default="Online")
    Broker_Agency_Type: str = Field(default="Large")
    Broker_ID: Optional[float] = Field(default=9.0)
    Employer_ID: Optional[float] = Field(default=174.0)

    # Timeline
    Policy_Start_Year: int = Field(default=2024, ge=2000, le=2026)
    Policy_Start_Month: str = Field(default="January")
    Policy_Start_Week: int = Field(default=1, ge=1, le=53)
    Policy_Start_Day: int = Field(default=15, ge=1, le=31)


class PredictionResult(BaseModel):
    """Output schema for a prediction."""

    user_id: str
    predicted_bundle_id: int
    predicted_bundle_name: str
    confidence_scores: dict[str, float]
    bundle_meta: dict


class ModelInfo(BaseModel):
    """Schema for model metadata."""

    model_type: str
    n_classes: int
    n_features: int
    bundle_names: dict[int, str]
