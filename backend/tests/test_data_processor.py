"""Tests for data processing functionality."""

import pytest
from backend.services.data_processor import DataProcessor


def test_address_parsing():
    """Test address parsing functionality."""
    processor = DataProcessor()
    
    # Test normal address
    result = processor.parse_address("123 Main St, New York NY 10001")
    assert result["street"] == "123 Main St"
    assert result["city"] == "New York"
    assert result["state"] == "NY"
    assert result["zip_code"] == "10001"
    
    # Test address with apartment
    result = processor.parse_address("456 Oak Ave Apt 2B, Los Angeles CA 90028")
    assert "456 Oak Ave" in result["street"]
    assert result["city"] == "Los Angeles"
    assert result["state"] == "CA"
    
    # Test malformed address
    result = processor.parse_address("Invalid Address")
    assert result["street"] == "Invalid Address"
    assert result["city"] == ""
    assert result["state"] == ""


def test_coordinate_enrichment():
    """Test ZIP code to coordinate conversion."""
    processor = DataProcessor()
    
    # Test valid ZIP
    lat, lng = processor.enrich_with_coordinates("10001")
    assert lat is not None
    assert lng is not None
    assert 40 < lat < 41  # NYC latitude range
    assert -74 < lng < -73  # NYC longitude range
    
    # Test invalid ZIP
    lat, lng = processor.enrich_with_coordinates("00000")
    assert lat is None
    assert lng is None


def test_csv_validation():
    """Test CSV schema validation."""
    import pandas as pd
    processor = DataProcessor()
    
    # Test valid schema
    df = pd.DataFrame({
        "order_id": ["1", "2"],
        "order_date": ["2024-01-01", "2024-01-02"],
        "customer_name": ["John Doe", "Jane Smith"],
        "address_line": ["123 Main St", "456 Oak Ave"],
        "item_sku": ["SKU001", "SKU002"],
        "item_name": ["Item 1", "Item 2"],
        "quantity": [1, 2],
        "unit_price_usd": [10.00, 20.00]
    })
    
    errors = processor.validate_csv_schema(df)
    assert len(errors) == 0
    
    # Test missing columns
    df_invalid = pd.DataFrame({
        "order_id": ["1", "2"],
        "customer_name": ["John Doe", "Jane Smith"]
    })
    
    errors = processor.validate_csv_schema(df_invalid)
    assert len(errors) > 0
    assert "Missing required columns" in errors[0]