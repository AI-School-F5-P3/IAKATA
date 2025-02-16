from pydantic import BaseModel

class FormData(BaseModel):
    name: str = None
    description: str

class ResponseOutput(BaseModel):
    status: str
    message: str
    data: dict

class Context(BaseModel):
    pass