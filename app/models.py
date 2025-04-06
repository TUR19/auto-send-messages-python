from pydantic import BaseModel, Field, field_validator
from typing import Literal

class MessageRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20)
    message: str = Field(..., min_length=1)
    channel: Literal["whatsapp", "telegram", "both"]
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.replace(" ", "")
        if not cleaned.isdigit() or not cleaned.startswith("7"):
            raise ValueError("Номер должен начинаться с 7 и содержать только цифры")
        return cleaned