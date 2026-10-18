from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException,status

from app.api.routers import shipment
from app.api.schemas.shipment import ShipmentCreate,ShipmentUpdate
from app.database.models import DeliveryPartner, Seller, ShipmentStatus
from  app.database.models import Shipment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.services.base import BaseService
from app.services.shipment_event import ShipmentEventService
from .delivery_partner import DeliveryPartnerServices

class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerServices,
        event_service:ShipmentEventService
    ):
        super().__init__(Shipment,session)
        self.partner_service = partner_service
        self.event_service=event_service

    async def get(self,id:UUID)-> Shipment | None:
        result = await self.session.execute(
        select(Shipment)
        .options(selectinload(Shipment.timeline),selectinload(Shipment.seller),)
        .where(Shipment.id == id)
    )
        return result.scalar_one_or_none()

    async def add(self,shipmennt_create: ShipmentCreate,seller:Seller)->Shipment:
        new_shipment=Shipment(
            **shipmennt_create.model_dump(),
            estimated_delivery=datetime.now(timezone.utc) + timedelta(days=3),
            seller_id=seller.id,
        )
        partner =await self.partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner_id=partner.id
        shipment=await self._add(new_shipment)

        event=await self.event_service.add(
            shipment=shipment,
            location=new_shipment.destination,
            status=ShipmentStatus.placed,
            description=f"assigned to {partner.name}"
        )
        shipment.timeline.append(event)
        return shipment

    async def update(self,id:UUID,shipment_update:ShipmentUpdate,partner:DeliveryPartner)->Shipment:
        shipment=await self.get(id)
        if shipment is None:
            raise HTTPException(
            status_code=404,
            detail="Shipment not found",
            )
        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="NOT authorised",
            )

        update =shipment_update.model_dump(exclude_none=True)

        if shipment_update.estimated_delivery:
            shipment.estimated_delivery = shipment_update.estimated_delivery

        if "estimated_delivery" in update:
            shipment.estimated_delivery = update.pop("estimated_delivery")

        if update:
            await self.event_service.add(
                shipment=shipment,
                **update,
            )
        
        return await self._update(shipment)

    async def cancel(self,id:UUID,seller:Seller)->Shipment:
        shipment=await self.get(id)
        if shipment is None:
            raise HTTPException(
            status_code=404,
            detail="Shipment not found",
            )
        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="NOt AUTHORIZED",
            )
        event= await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
        )
        shipment.timeline.append(event)
        return shipment
    async def delete(self,id:UUID)->None:
        shipment = await self.session.get(Shipment, id)
        if shipment is None:
            raise HTTPException(
            status_code=404,
            detail="Shipment not found",
            )
        await self._delete(shipment)
