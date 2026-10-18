from typing import Annotated
from app.database.models import Seller
from app.utils import decode_access_token
from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import oauth2_scheme_partner
from app.api.dependencies import SellerServiceDep, SessionDep, get_partner_access_token
from ..schemas.delivery_partner import DeliveryPartnerCreate,DeliveryPartnerRead
from app.database.redis import add_jti_to_blacklist
from ..dependencies import DeliveryPartnerDep, DeliveryPartnerServiceDep,get_partner_access_token
from ..schemas.delivery_partner import DeliveryPartnerUpdate
router =APIRouter(prefix="/partner",tags=["Deliver Partner"])

@router.post("/signup",response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    seller:DeliveryPartnerCreate , service: DeliveryPartnerServiceDep
):
    return await service.add(seller)

@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm,Depends()],
    service:DeliveryPartnerServiceDep,
):
    token = await service.token(request_form.username,request_form.password)
    return{
        "access_token":token,
        "token_type":"jwt",
    } 


@router.get("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict,Depends(get_partner_access_token)]
):
   await add_jti_to_blacklist(token_data["jti"])
   return {
       "detail": "Successfully logged out"
   }

@router.post("/",response_model=DeliveryPartnerRead)
async def update_delivery_partner(
    partner_update:DeliveryPartnerUpdate,
    partner:DeliveryPartnerDep,
    service:DeliveryPartnerServiceDep,
): 
    update = partner_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    
    return await service.update(
    partner.sqlmodel_update(update)
)