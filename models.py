from pydantic import BaseModel

class MessageRequest(BaseModel):
    to: str
    message: str
    


class SingleMessageRequest(BaseModel):
    phone_number: str
    full_name: str
    location:str
    qualification:str