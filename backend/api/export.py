"""Export endpoints."""

import io
from typing import Optional
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse

from core.database import get_connection
from core.security import require_role


router = APIRouter()


@router.get("/excel")
async def export_to_excel(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    state: Optional[str] = Query(None),
    item_sku: Optional[str] = Query(None),
    _: dict = Depends(require_role("viewer"))
):
    """Export filtered orders to Excel."""
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
    
    # Build final query
    query = """
        SELECT 
            order_id,
            order_date,
            customer_name,
            address_line,
            city,
            state,
            zip_code,
            item_sku,
            item_name,
            quantity,
            unit_price_usd,
            order_total
        FROM orders
    """
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY order_date DESC"
    
    # Execute query
    df = conn.execute(query, params).fetchdf()
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Orders', index=False)
        
        # Get the worksheet
        worksheet = writer.sheets['Orders']
        
        # Style the header row
        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)
            cell.fill = cell.fill.copy(fgColor="E0E0E0")
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"order_analytics_{timestamp}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )