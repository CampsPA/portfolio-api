from pydantic import BaseModel, ConfigDict
from datetime import datetime


class HoldingCreate(BaseModel):
    ticker : str
    num_shares : float 
    average_cost : float | None = None


class HoldingUpdate(BaseModel):
    num_shares : float | None = None
    average_cost : float | None = None


class HoldingResponse(BaseModel):
    id : int
    portfolio_id : int
    ticker : str
    num_shares : float 
    average_cost : float
    created_at : datetime

    model_config = ConfigDict(from_attributes=True) 