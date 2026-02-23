from pydantic import BaseModel, ConfigDict
from datetime import datetime



class PortfolioCreate(BaseModel):
    name : str
    description : str | None = None # optional field


class PortfolioUpdate(BaseModel):
    name : str | None = None         # optional field
    description : str | None = None  # optional field


class PortfolioResponse(BaseModel):
    id : int
    name : str
    description : str | None = None # optional field
    user_id : int
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)