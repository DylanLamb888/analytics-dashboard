"""Metrics and analytics endpoints."""

from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Query, Depends

from core.database import get_connection
from core.security import require_role
from schemas.metrics import (
    DashboardMetrics,
    SalesMetrics,
    ProductMetrics,
    TimeSeriesMetric,
    GeographicMetric
)


router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    _: dict = Depends(require_role("viewer"))
):
    """Get comprehensive dashboard metrics."""
    conn = get_connection()
    
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get sales metrics
    sales_metrics = _get_sales_metrics(conn, start_date, end_date)
    
    # Get top products
    top_products = _get_top_products(conn, start_date, end_date)
    
    # Get time series data
    time_series = _get_time_series(conn, start_date, end_date)
    
    # Get geographic distribution
    geographic_distribution = _get_geographic_distribution(conn, start_date, end_date)
    
    return DashboardMetrics(
        sales_metrics=sales_metrics,
        top_products=top_products,
        time_series=time_series,
        geographic_distribution=geographic_distribution
    )


def _get_sales_metrics(conn, start_date: datetime, end_date: datetime) -> SalesMetrics:
    """Calculate overall sales metrics."""
    query = """
        SELECT 
            SUM(order_total) as total_revenue,
            COUNT(DISTINCT order_id) as total_orders,
            SUM(quantity) as total_items_sold,
            AVG(order_total) as avg_order_value,
            COUNT(DISTINCT customer_name) as unique_customers,
            COUNT(DISTINCT state) as unique_states,
            MIN(order_date) as first_order,
            MAX(order_date) as last_order
        FROM orders
        WHERE order_date >= ? AND order_date <= ?
    """
    
    result = conn.execute(query, [start_date, end_date]).fetchone()
    
    return SalesMetrics(
        total_revenue=Decimal(str(result[0] or 0)),
        total_orders=result[1] or 0,
        total_items_sold=result[2] or 0,
        average_order_value=Decimal(str(result[3] or 0)),
        unique_customers=result[4] or 0,
        unique_states=result[5] or 0,
        date_range={
            "start": start_date.date(),
            "end": end_date.date()
        }
    )


def _get_top_products(conn, start_date: datetime, end_date: datetime, limit: int = 10) -> list[ProductMetrics]:
    """Get top selling products."""
    query = """
        SELECT 
            item_sku,
            item_name,
            SUM(quantity) as quantity_sold,
            SUM(order_total) as revenue,
            COUNT(DISTINCT order_id) as order_count
        FROM orders
        WHERE order_date >= ? AND order_date <= ?
        GROUP BY item_sku, item_name
        ORDER BY revenue DESC
        LIMIT ?
    """
    
    results = conn.execute(query, [start_date, end_date, limit]).fetchall()
    
    # Get total revenue for percentage calculation
    total_revenue_query = """
        SELECT SUM(order_total) FROM orders 
        WHERE order_date >= ? AND order_date <= ?
    """
    total_revenue = conn.execute(total_revenue_query, [start_date, end_date]).fetchone()[0] or 1
    
    products = []
    for row in results:
        products.append(ProductMetrics(
            item_sku=row[0],
            item_name=row[1],
            quantity_sold=row[2],
            revenue=Decimal(str(row[3])),
            order_count=row[4],
            percentage_of_total=float(row[3]) / float(total_revenue) * 100
        ))
    
    return products


def _get_time_series(conn, start_date: datetime, end_date: datetime) -> list[TimeSeriesMetric]:
    """Get daily time series data."""
    query = """
        SELECT 
            order_day,
            SUM(order_total) as daily_revenue,
            COUNT(DISTINCT order_id) as daily_orders,
            SUM(quantity) as daily_items
        FROM orders
        WHERE order_date >= ? AND order_date <= ?
        GROUP BY order_day
        ORDER BY order_day
    """
    
    results = conn.execute(query, [start_date, end_date]).fetchall()
    
    time_series = []
    for row in results:
        time_series.append(TimeSeriesMetric(
            date=row[0],
            revenue=Decimal(str(row[1])),
            order_count=row[2],
            items_sold=row[3]
        ))
    
    return time_series


def _get_geographic_distribution(conn, start_date: datetime, end_date: datetime) -> list[GeographicMetric]:
    """Get geographic distribution by state."""
    query = """
        SELECT 
            state,
            SUM(order_total) as revenue,
            COUNT(DISTINCT order_id) as order_count,
            AVG(latitude) as avg_lat,
            AVG(longitude) as avg_lng
        FROM orders
        WHERE order_date >= ? AND order_date <= ?
        AND state IS NOT NULL AND state != ''
        GROUP BY state
        ORDER BY revenue DESC
    """
    
    results = conn.execute(query, [start_date, end_date]).fetchall()
    
    # Get total revenue for percentage
    total_revenue_query = """
        SELECT SUM(order_total) FROM orders 
        WHERE order_date >= ? AND order_date <= ?
    """
    total_revenue = conn.execute(total_revenue_query, [start_date, end_date]).fetchone()[0] or 1
    
    geographic = []
    for row in results:
        geographic.append(GeographicMetric(
            location=row[0],
            location_type="state",
            revenue=Decimal(str(row[1])),
            order_count=row[2],
            percentage_of_total=float(row[1]) / float(total_revenue) * 100,
            latitude=row[3],
            longitude=row[4]
        ))
    
    return geographic