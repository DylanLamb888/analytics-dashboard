"""Order management endpoints."""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Query, Depends, HTTPException

from core.database import get_connection
from core.security import require_role
from schemas.orders import OrdersResponse, OrdersFilter


router = APIRouter()


@router.get("", response_model=OrdersResponse)
async def get_orders(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    state: Optional[str] = Query(None),
    item_sku: Optional[str] = Query(None),
    min_total: Optional[float] = Query(None),
    max_total: Optional[float] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_role("viewer"))
):
    """Get filtered orders."""
    conn = get_connection()
    
    # Build query
    where_clauses = []
    params = []
    
    if start_date:
        where_clauses.append("order_date >= ?")
        params.append(start_date)
    
    if end_date:
        where_clauses.append("order_date <= ?")
        params.append(end_date)
    
    if state:
        where_clauses.append("state = ?")
        params.append(state)
    
    if item_sku:
        where_clauses.append("item_sku = ?")
        params.append(item_sku)
    
    if min_total is not None:
        where_clauses.append("order_total >= ?")
        params.append(min_total)
    
    if max_total is not None:
        where_clauses.append("order_total <= ?")
        params.append(max_total)
    
    # Build final query
    base_query = "SELECT * FROM orders"
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    
    # Get total count
    total_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    
    # Get filtered count
    count_query = f"SELECT COUNT(*) FROM ({base_query}) t"
    filtered_count = conn.execute(count_query, params).fetchone()[0]
    
    # Get paginated results
    query = f"{base_query} ORDER BY order_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    result = conn.execute(query, params).fetchdf()
    
    # Convert to dict records
    orders = result.to_dict('records') if not result.empty else []
    
    return OrdersResponse(
        orders=orders,
        total_count=total_count,
        filtered_count=filtered_count
    )