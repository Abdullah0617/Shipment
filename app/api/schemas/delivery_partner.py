from pydantic import BaseModel, EmailStr, Field

class BaseDeliveryPartner(BaseModel):
    name:str
    email: EmailStr
    serviceable_zip_codes:list[int]
    max_handeling_capacity:int


class DeliveryPartnerCreate(BaseDeliveryPartner):
    password:str

class DeliveryPartnerRead(BaseDeliveryPartner):
    pass

class DeliveryPartnerUpdate(BaseModel):
    serviceable_zip_code:list[int] |None = Field(default=None)
    max_handeling_capacity:int|None = Field(default=None)