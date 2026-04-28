from pydantic import BaseModel
from typing import Optional, List

class RouteSchema(BaseModel):
    source: str
    target: str
    time: float
    cost: float
    distance: float

class DecisionSchema(BaseModel):
    action: str
    risk_score: float
    recommended_path: Optional[List[str]]
    reason: str

class SimulateResponse(BaseModel):
    prediction: dict
    decision: DecisionSchema
