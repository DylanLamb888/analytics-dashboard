"""File upload endpoints."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status

from core.config import settings
from core.security import require_role
from core.database import clear_orders
from services.data_processor import data_processor


router = APIRouter()


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    _: dict = Depends(require_role("admin"))
):
    """Upload and process CSV file."""
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB limit"
        )
    
    # Clear existing orders
    clear_orders()
    
    # Process CSV
    result = data_processor.process_csv(contents)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Failed to process CSV file",
                "errors": result['errors']
            }
        )
    
    return {
        "success": True,
        "rows_processed": result['rows_processed'],
        "message": f"Successfully processed {result['rows_processed']} orders"
    }