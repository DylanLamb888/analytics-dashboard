"""Data processing service for CSV files."""

import io
from typing import List, Dict, Any, Tuple
from datetime import datetime

import pandas as pd
import usaddress

from core.database import get_connection
from schemas.orders import OrderCreate
from services.zipcode_data import get_coordinates_for_zip


class DataProcessor:
    """Service for processing order data."""
    
    def __init__(self):
        pass
    
    def parse_address(self, address_line: str) -> Dict[str, str]:
        """Parse address into components."""
        try:
            # Parse address using usaddress
            parsed, address_type = usaddress.tag(address_line)
            
            # Extract components
            street_parts = []
            if parsed.get('AddressNumber'):
                street_parts.append(parsed['AddressNumber'])
            if parsed.get('StreetNamePreDirectional'):
                street_parts.append(parsed['StreetNamePreDirectional'])
            if parsed.get('StreetName'):
                street_parts.append(parsed['StreetName'])
            if parsed.get('StreetNamePostType'):
                street_parts.append(parsed['StreetNamePostType'])
            
            street = ' '.join(street_parts)
            city = parsed.get('PlaceName', '')
            state = parsed.get('StateName', '')
            zip_code = parsed.get('ZipCode', '')
            
            return {
                'street': street,
                'city': city,
                'state': state,
                'zip_code': zip_code,
            }
        except Exception:
            # Fallback parsing
            parts = address_line.split(',')
            if len(parts) >= 2:
                street = parts[0].strip()
                city_state_zip = parts[1].strip()
                
                # Try to extract city, state, zip
                tokens = city_state_zip.split()
                if len(tokens) >= 3:
                    zip_code = tokens[-1]
                    state = tokens[-2]
                    city = ' '.join(tokens[:-2])
                else:
                    city = city_state_zip
                    state = ''
                    zip_code = ''
                
                return {
                    'street': street,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code,
                }
            
            return {
                'street': address_line,
                'city': '',
                'state': '',
                'zip_code': '',
            }
    
    def enrich_with_coordinates(self, zip_code: str) -> Tuple[float, float]:
        """Get latitude and longitude for ZIP code."""
        lat, lng = get_coordinates_for_zip(zip_code)
        return lat, lng
    
    def validate_csv_schema(self, df: pd.DataFrame) -> List[str]:
        """Validate CSV schema and return errors."""
        required_columns = [
            'order_id', 'order_date', 'customer_name', 'address_line',
            'item_sku', 'item_name', 'quantity', 'unit_price_usd'
        ]
        
        errors = []
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate data types if columns exist
        if 'quantity' in df.columns:
            try:
                df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
                if df['quantity'].isna().any():
                    errors.append("Invalid quantity values found")
            except Exception:
                errors.append("Could not convert quantity to numeric")
        
        if 'unit_price_usd' in df.columns:
            try:
                df['unit_price_usd'] = pd.to_numeric(df['unit_price_usd'], errors='coerce')
                if df['unit_price_usd'].isna().any():
                    errors.append("Invalid unit_price_usd values found")
            except Exception:
                errors.append("Could not convert unit_price_usd to numeric")
        
        if 'order_date' in df.columns:
            try:
                pd.to_datetime(df['order_date'])
            except Exception:
                errors.append("Invalid date format in order_date column")
        
        return errors
    
    def process_csv(self, file_content: bytes) -> Dict[str, Any]:
        """Process CSV file and return results."""
        try:
            # Read CSV
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Validate schema
            errors = self.validate_csv_schema(df)
            if errors:
                return {
                    'success': False,
                    'errors': errors,
                    'rows_processed': 0,
                }
            
            # Clean data
            df = df.drop_duplicates(subset=['order_id'])
            df = df.dropna(subset=['order_id', 'order_date', 'customer_name', 'address_line'])
            
            # Process each row
            processed_rows = []
            for _, row in df.iterrows():
                # Parse address
                address_parts = self.parse_address(row['address_line'])
                
                # Get coordinates
                lat, lng = self.enrich_with_coordinates(address_parts['zip_code'])
                
                # Calculate derived fields
                order_date = pd.to_datetime(row['order_date'])
                order_total = float(row['quantity']) * float(row['unit_price_usd'])
                
                processed_row = {
                    'order_id': str(row['order_id']),
                    'order_date': order_date,
                    'customer_name': row['customer_name'],
                    'address_line': row['address_line'],
                    'street': address_parts['street'],
                    'city': address_parts['city'],
                    'state': address_parts['state'],
                    'zip_code': address_parts['zip_code'],
                    'latitude': lat,
                    'longitude': lng,
                    'item_sku': row['item_sku'],
                    'item_name': row['item_name'],
                    'quantity': int(row['quantity']),
                    'unit_price_usd': float(row['unit_price_usd']),
                    'order_total': order_total,
                    'order_day': order_date.date(),
                    'weekday': order_date.weekday(),
                }
                
                processed_rows.append(processed_row)
            
            # Insert into database
            if processed_rows:
                self._insert_orders(processed_rows)
            
            return {
                'success': True,
                'rows_processed': len(processed_rows),
                'errors': [],
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'rows_processed': 0,
            }
    
    def _insert_orders(self, orders: List[Dict[str, Any]]):
        """Insert orders into database."""
        conn = get_connection()
        
        # Convert to DataFrame for bulk insert
        df = pd.DataFrame(orders)
        
        # Insert into DuckDB
        conn.execute("INSERT INTO orders SELECT * FROM df")
        conn.commit()


# Singleton instance
data_processor = DataProcessor()