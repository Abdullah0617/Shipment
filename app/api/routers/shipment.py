from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from app.api.dependencies import DeliveryPartnerDep, SellerDep, ServiceDep
from app.database.models import Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate

router = APIRouter(prefix="/shipment", tags=["Shipment"])


@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: UUID,_:SellerDep, service: ServiceDep):
    shipment = await service.get(id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given shipment ID not found"
        )
    return shipment


@router.post("/",response_model=ShipmentRead)
async def post_shipment(
    seller:SellerDep,
    shipment: ShipmentCreate,
    service: ServiceDep,
) -> Shipment:
    return await service.add(shipment,seller)


@router.patch(
    "/",
    response_model=ShipmentRead,
)
async def patch_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner :DeliveryPartnerDep,
    service: ServiceDep,
):
    update = shipment_update.model_dump(exclude_none=True)
    print("UPDATE DATA:", update)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    return await service.update(id, shipment_update,partner)


@router.get("/cancel",response_model=ShipmentRead)
async def cancel_shipment(id: UUID,seller:SellerDep ,service: ServiceDep) -> dict[str, str]:

   return await service.cancel(id,seller)

