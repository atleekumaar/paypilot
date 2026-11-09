"""Channel3 integration package."""

from app.services.channel3.client import (
    Channel3Client,
    Channel3Config,
    Channel3Product,
    Channel3ProductVariant,
)
from app.services.channel3.service import (
    Channel3Service,
    channel3_to_paypilot_product,
    get_channel3_service,
)

__all__ = [
    "Channel3Client",
    "Channel3Config",
    "Channel3Product",
    "Channel3ProductVariant",
    "Channel3Service",
    "channel3_to_paypilot_product",
    "get_channel3_service",
]

