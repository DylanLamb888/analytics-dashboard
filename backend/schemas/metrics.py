"""Metrics schemas."""

from datetime import date
from typing import List, Dict, Any, Optional
from decimal import Decimal

from pydantic import BaseModel


class SalesMetrics(BaseModel):
    """Overall sales metrics."""
    total_revenue: Decimal
    total_orders: int
    total_items_sold: int
    average_order_value: Decimal
    unique_customers: int
    unique_states: int
    date_range: Dict[str, date]


class ProductMetrics(BaseModel):
    """Product performance metrics."""
    item_sku: str
    item_name: str
    quantity_sold: int
    revenue: Decimal
    order_count: int
    percentage_of_total: float


class TimeSeriesMetric(BaseModel):
    """Time series data point."""
    date: date
    revenue: Decimal
    order_count: int
    items_sold: int


class GeographicMetric(BaseModel):
    """Geographic distribution metric."""
    location: str
    location_type: str  # "state" or "zip"
    revenue: Decimal
    order_count: int
    percentage_of_total: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DashboardMetrics(BaseModel):
    """Complete dashboard metrics response."""
    sales_metrics: SalesMetrics
    top_products: List[ProductMetrics]
    time_series: List[TimeSeriesMetric]
    geographic_distribution: List[GeographicMetric]