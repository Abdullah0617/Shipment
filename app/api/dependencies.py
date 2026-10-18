from typing import Annotated
from fastapi import Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import DeliveryPartner, Seller
from app.database.redis import is_jti_blacklisted
from app.database.session import get_session
from app.services.shipment import ShipmentService
from app.services.seller import SellerService
from app.core.security import oauth2_scheme_partner, oauth2_scheme_seller
from app.services.shipment_event import ShipmentEventService
from app.utils import decode_access_token
from app.services.delivery_partner import DeliveryPartnerServices

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_shipment_service(session: SessionDep):
    return ShipmentService(
        session, DeliveryPartnerServices(session), ShipmentEventService(session)
    )


def get_seller_service(session: SessionDep):
    return SellerService(session)


def get_delivery_partner_service(session: SessionDep):
    return DeliveryPartnerServices(session)


ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]


async def _get_access_token(token: str):
    print("TOKEN RECEIVED:", repr(token))
    token = token.split(",")[0].strip()
    print("CLEAN TOKEN:", repr(token))

    data = decode_access_token(token)

    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired access token",
        )
    print("DECODED:", data)
    return data


async def get_seller_access_token(
    token: Annotated[str, Depends(oauth2_scheme_seller)],
) -> dict:
    return await _get_access_token(token)


async def get_partner_access_token(
    token: Annotated[str, Depends(oauth2_scheme_partner)],
) -> dict:
    return await _get_access_token(token)


async def get_current_seller(
    token_data: Annotated[dict, Depends(get_seller_access_token)], session: SessionDep
):
    seller = await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorixed",
        )
    return seller


async def get_current_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)], session: SessionDep
):
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))
    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorixed",
        )
    return partner


SellerDep = Annotated[Seller, Depends(get_current_seller)]

DeliveryPartnerDep = Annotated[DeliveryPartner, Depends(get_current_partner)]

DeliveryPartnerServiceDep = Annotated[
    DeliveryPartnerServices,
    Depends(get_delivery_partner_service),
]
