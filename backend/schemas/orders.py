"""Order-related schemas."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderBase(BaseModel):
    """Base order schema."""
    order_id: str
    order_date: datetime
    customer_name: str
    address_line: str
    item_sku: str
    item_name: str
    quantity: int = Field(gt=0)
    unit_price_usd: Decimal = Field(gt=0, decimal_places=2)


class OrderCreate(OrderBase):
    """Schema for creating orders."""
    pass


class Order(OrderBase):
    """Complete order schema with computed fields."""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    order_total: Decimal
    order_day: date
    weekday: int
    upload_timestamp: datetime

    class Config:
        from_attributes = True


class OrdersFilter(BaseModel):
    """Filter parameters for orders."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    state: Optional[str] = None
    item_sku: Optional[str] = None
    min_total: Optional[Decimal] = None
    max_total: Optional[Decimal] = None


class OrdersResponse(BaseModel):
    """Response schema for orders list."""
    orders: List[Order]
    total_count: int
    filtered_count: int