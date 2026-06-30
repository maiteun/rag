from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    code: str
    message: str


class MessageResponse(BaseModel):
    message: str


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

