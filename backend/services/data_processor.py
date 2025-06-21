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
            # Read CSV with proper handling of quoted fields
            df = pd.read_csv(io.BytesIO(file_content), quotechar='"', skipinitialspace=True)
            
            # Log for debugging
            print(f"CSV loaded with {len(df)} rows")
            print(f"Columns: {df.columns.tolist()}")
            
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
            failed_rows = []
            
            for idx, row in df.iterrows():
                try:
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
                except Exception as row_error:
                    failed_rows.append({
                        'row': idx + 2,  # +2 for header and 0-based index
                        'order_id': row.get('order_id', 'unknown'),
                        'error': str(row_error)
                    })
                    print(f"Error processing row {idx}: {row_error}")
            
            # Insert into database
            if processed_rows:
                self._insert_orders(processed_rows)
            
            # Return results with details about failures
            result = {
                'success': len(processed_rows) > 0,
                'rows_processed': len(processed_rows),
                'errors': [],
            }
            
            if failed_rows:
                result['errors'].append(f"Failed to process {len(failed_rows)} rows")
                if len(failed_rows) <= 5:
                    for fail in failed_rows:
                        result['errors'].append(f"Row {fail['row']} (Order {fail['order_id']}): {fail['error']}")
            
            return result
            
        except Exception as e:
            print(f"CSV processing error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'errors': [f"CSV processing failed: {str(e)}"],
                'rows_processed': 0,
            }
    
    def _insert_orders(self, orders: List[Dict[str, Any]]):
        """Insert orders into database."""
        conn = get_connection()
        
        # Convert to DataFrame for bulk insert
        df = pd.DataFrame(orders)
        
        # Specify columns explicitly to avoid mismatch
        columns = [
            'order_id', 'order_date', 'customer_name', 'address_line',
            'street', 'city', 'state', 'zip_code', 'latitude', 'longitude',
            'item_sku', 'item_name', 'quantity', 'unit_price_usd',
            'order_total', 'order_day', 'weekday'
        ]
        
        # Create column list for SQL
        column_list = ', '.join(columns)
        
        # Insert into DuckDB with explicit columns
        conn.execute(f"""
            INSERT INTO orders ({column_list})
            SELECT {column_list} FROM df
        """)
        conn.commit()


# Singleton instance
data_processor = DataProcessor()