from fastapi import HTTPException,status
from sqlalchemy.orm import selectinload
from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from app.database.models import DeliveryPartner, Shipment
from .user import UserService
from typing import Sequence
from sqlalchemy import select, any_
class DeliveryPartnerServices(UserService):
    def __init__(self, session):
        super().__init__(DeliveryPartner, session)

    async def  add(self,delivery_partner:DeliveryPartnerCreate):
        return await self._add_user(
            delivery_partner.model_dump()
        )

    async def token(self,email,password)-> str:
        return await self._generate_token(email,password)

    async def update(self,partner:DeliveryPartner):
        return await self._update(partner)

    async def get_partner_by_zipcode(self,zipcode:int)->Sequence[DeliveryPartner]:
        result = await  self.session.execute(
            select(DeliveryPartner).options(selectinload(DeliveryPartner.shipments).selectinload(Shipment.timeline)).where(
                zipcode==any_(DeliveryPartner.serviceable_zip_codes)
            )
        )
        eligible_partner=result.scalars().all()
        return eligible_partner

    
    async def assign_shipment(self,shipment:Shipment):
        eligible_partner=await self.get_partner_by_zipcode(shipment.destination)

        for partner in eligible_partner:
            if partner.current_handling_capacity>0:
                shipment.delivery_partner=partner
                return  partner

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No delivery partner available",
        )    