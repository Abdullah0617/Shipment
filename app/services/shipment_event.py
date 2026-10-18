from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService
from sqlalchemy import select
from app.database.models import Shipment, ShipmentEvent

class ShipmentEventService(BaseService):
    def __init__(self,session):
        super().__init__(ShipmentEvent,session)


    async def add(
        self,
        shipment:Shipment,
        location:int |None= None,
        status:ShipmentStatus|None= None,
        description:str |None= None,
    )->ShipmentEvent:  

        if location is None or status is None:
            last_event = await self.get_latest_event(shipment)

            if last_event is not None:
                if location is None:
                    location = last_event.location

                if status is None:
                    status = last_event.status

        if location is None or status is None:
            raise ValueError(
                "Location and status are required for the first event"
            )

        new_event=ShipmentEvent(
            location=location,
            status=status,
            description=description if description is not None else self._generate_description(status ,location),
            shipment_id=shipment.id,
        )
        
        return await self._add(new_event)
        
    async def get_latest_event(self,shipment:Shipment):
        result = await self.session.execute(
            select(ShipmentEvent) 
            .where(
                ShipmentEvent.shipment_id == shipment.id
            )
            .order_by(ShipmentEvent.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    def _generate_description(self,status:ShipmentStatus,location:int):
        match status:
            case ShipmentStatus.placed:
                return "assigned deliver partner"
            case ShipmentStatus.in_transit:
                return f"scanned at {location}"
            case ShipmentStatus.delivered:
                return "successfully deliverd"
            case ShipmentStatus.cancelled:
                return "cancelled by the seller"
