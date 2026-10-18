from pydantic import BaseModel, EmailStr

class SellerBase(BaseModel):
    name:str
    email: EmailStr


class SellerCreate(SellerBase):
    password:str

class SellerRead(SellerBase):
    pass