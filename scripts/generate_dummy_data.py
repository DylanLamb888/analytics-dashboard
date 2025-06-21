#!/usr/bin/env python3
"""Generate dummy order data for the analytics dashboard prototype."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Configuration
NUM_ORDERS = 1000
NUM_CUSTOMERS = 200
OUTPUT_FILE = "dummy_orders.csv"

# Product catalog
PRODUCTS = [
    {"sku": "SKU-A12-BLK", "name": "Transit Backpack", "price": 79.00},
    {"sku": "SKU-B23-GRY", "name": "Urban Messenger Bag", "price": 65.00},
    {"sku": "SKU-C34-NVY", "name": "Executive Briefcase", "price": 125.00},
    {"sku": "SKU-D45-BRN", "name": "Leather Wallet", "price": 45.00},
    {"sku": "SKU-E56-BLK", "name": "Travel Duffel", "price": 95.00},
    {"sku": "SKU-F67-RED", "name": "Sports Backpack", "price": 55.00},
    {"sku": "SKU-G78-BLU", "name": "Laptop Sleeve", "price": 35.00},
    {"sku": "SKU-H89-GRN", "name": "Camera Bag", "price": 85.00},
]

# US addresses data
ADDRESSES = [
    # California
    {"street": "123 Market St", "city": "San Francisco", "state": "CA", "zip": "94103"},
    {"street": "456 Sunset Blvd", "city": "Los Angeles", "state": "CA", "zip": "90028"},
    {"street": "789 Ocean Ave", "city": "San Diego", "state": "CA", "zip": "92101"},
    {"street": "321 Pine St", "city": "San Francisco", "state": "CA", "zip": "94108"},
    {"street": "654 Hollywood Blvd", "city": "Los Angeles", "state": "CA", "zip": "90038"},
    
    # New York
    {"street": "100 Broadway", "city": "New York", "state": "NY", "zip": "10005"},
    {"street": "200 5th Ave", "city": "New York", "state": "NY", "zip": "10010"},
    {"street": "300 Park Ave", "city": "New York", "state": "NY", "zip": "10022"},
    {"street": "400 Madison Ave", "city": "New York", "state": "NY", "zip": "10017"},
    {"street": "500 Lexington Ave", "city": "New York", "state": "NY", "zip": "10170"},
    
    # Texas
    {"street": "111 Congress Ave", "city": "Austin", "state": "TX", "zip": "78701"},
    {"street": "222 Main St", "city": "Houston", "state": "TX", "zip": "77002"},
    {"street": "333 Commerce St", "city": "Dallas", "state": "TX", "zip": "75201"},
    {"street": "444 Travis St", "city": "Houston", "state": "TX", "zip": "77002"},
    {"street": "555 Elm St", "city": "Dallas", "state": "TX", "zip": "75202"},
    
    # Florida
    {"street": "101 Ocean Dr", "city": "Miami Beach", "state": "FL", "zip": "33139"},
    {"street": "202 Collins Ave", "city": "Miami Beach", "state": "FL", "zip": "33140"},
    {"street": "303 Biscayne Blvd", "city": "Miami", "state": "FL", "zip": "33132"},
    {"street": "404 Orange Ave", "city": "Orlando", "state": "FL", "zip": "32801"},
    {"street": "505 Beach Blvd", "city": "Jacksonville", "state": "FL", "zip": "32250"},
    
    # Illinois
    {"street": "123 N Michigan Ave", "city": "Chicago", "state": "IL", "zip": "60601"},
    {"street": "234 W Madison St", "city": "Chicago", "state": "IL", "zip": "60606"},
    {"street": "345 N State St", "city": "Chicago", "state": "IL", "zip": "60654"},
    {"street": "456 S Wacker Dr", "city": "Chicago", "state": "IL", "zip": "60606"},
    {"street": "567 E Grand Ave", "city": "Chicago", "state": "IL", "zip": "60611"},
    
    # Washington
    {"street": "100 Pike St", "city": "Seattle", "state": "WA", "zip": "98101"},
    {"street": "200 1st Ave", "city": "Seattle", "state": "WA", "zip": "98104"},
    {"street": "300 University St", "city": "Seattle", "state": "WA", "zip": "98101"},
    {"street": "400 Pine St", "city": "Seattle", "state": "WA", "zip": "98101"},
    {"street": "500 Broadway", "city": "Seattle", "state": "WA", "zip": "98122"},
    
    # Massachusetts
    {"street": "100 Summer St", "city": "Boston", "state": "MA", "zip": "02110"},
    {"street": "200 State St", "city": "Boston", "state": "MA", "zip": "02109"},
    {"street": "300 Congress St", "city": "Boston", "state": "MA", "zip": "02210"},
    {"street": "400 Atlantic Ave", "city": "Boston", "state": "MA", "zip": "02110"},
    {"street": "500 Boylston St", "city": "Boston", "state": "MA", "zip": "02116"},
    
    # Colorado
    {"street": "123 Maple St", "city": "Denver", "state": "CO", "zip": "80218"},
    {"street": "234 Broadway", "city": "Denver", "state": "CO", "zip": "80205"},
    {"street": "345 Lincoln St", "city": "Denver", "state": "CO", "zip": "80203"},
    {"street": "456 Pearl St", "city": "Boulder", "state": "CO", "zip": "80302"},
    {"street": "567 Canyon Blvd", "city": "Boulder", "state": "CO", "zip": "80302"},
    
    # Georgia
    {"street": "100 Peachtree St", "city": "Atlanta", "state": "GA", "zip": "30303"},
    {"street": "200 Marietta St", "city": "Atlanta", "state": "GA", "zip": "30303"},
    {"street": "300 Spring St", "city": "Atlanta", "state": "GA", "zip": "30308"},
    {"street": "400 Piedmont Ave", "city": "Atlanta", "state": "GA", "zip": "30308"},
    {"street": "500 North Ave", "city": "Atlanta", "state": "GA", "zip": "30308"},
    
    # Arizona
    {"street": "100 E Washington St", "city": "Phoenix", "state": "AZ", "zip": "85004"},
    {"street": "200 N Central Ave", "city": "Phoenix", "state": "AZ", "zip": "85004"},
    {"street": "300 E Van Buren St", "city": "Phoenix", "state": "AZ", "zip": "85004"},
    {"street": "400 Mill Ave", "city": "Tempe", "state": "AZ", "zip": "85281"},
    {"street": "500 University Dr", "city": "Tempe", "state": "AZ", "zip": "85281"},
]

# Customer names
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
               "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
               "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
               "Kenneth", "Laura", "Kevin", "Emily", "Brian", "Kimberly", "George", "Deborah",
               "Edward", "Dorothy", "Ronald", "Amy", "Timothy", "Angela", "Jason", "Ashley"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
              "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
              "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
              "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
              "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"]

def generate_customer_name():
    """Generate a random customer name."""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def generate_order_date():
    """Generate a random order date within the last 180 days."""
    days_ago = random.randint(0, 180)
    order_date = datetime.now() - timedelta(days=days_ago)
    # Add random time of day
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    order_date = order_date.replace(hour=hours, minute=minutes, second=seconds)
    return order_date.strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_orders():
    """Generate dummy order data."""
    orders = []
    
    # Generate unique customer names
    customers = []
    while len(customers) < NUM_CUSTOMERS:
        name = generate_customer_name()
        if name not in customers:
            customers.append(name)
    
    for _ in range(NUM_ORDERS):
        # Select random product
        product = random.choice(PRODUCTS)
        
        # Select random customer
        customer = random.choice(customers)
        
        # Select random address
        address = random.choice(ADDRESSES)
        address_line = f"{address['street']}, {address['city']} {address['state']} {address['zip']}"
        
        # Generate quantity (weighted towards 1-2 items)
        quantity_weights = [0.6, 0.25, 0.1, 0.05]
        quantity = random.choices([1, 2, 3, 4], weights=quantity_weights)[0]
        
        order = {
            "order_id": str(uuid.uuid4()),
            "order_date": generate_order_date(),
            "customer_name": customer,
            "address_line": address_line,
            "item_sku": product["sku"],
            "item_name": product["name"],
            "quantity": quantity,
            "unit_price_usd": product["price"]
        }
        
        orders.append(order)
    
    # Sort by date (newest first)
    orders.sort(key=lambda x: x["order_date"], reverse=True)
    
    return orders

def main():
    """Generate dummy data and save to CSV."""
    print("Generating dummy order data...")
    
    orders = generate_orders()
    
    # Write to CSV
    output_path = Path(__file__).parent.parent / OUTPUT_FILE
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["order_id", "order_date", "customer_name", "address_line", 
                     "item_sku", "item_name", "quantity", "unit_price_usd"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(orders)
    
    print(f"✓ Generated {len(orders)} orders")
    print(f"✓ Saved to: {output_path}")
    
    # Print summary statistics
    total_revenue = sum(order["quantity"] * order["unit_price_usd"] for order in orders)
    avg_order_value = total_revenue / len(orders)
    
    print(f"\nSummary:")
    print(f"  Total Revenue: ${total_revenue:,.2f}")
    print(f"  Average Order Value: ${avg_order_value:.2f}")
    print(f"  Unique Customers: {NUM_CUSTOMERS}")
    print(f"  Products: {len(PRODUCTS)}")
    print(f"  States: {len(set(addr['state'] for addr in ADDRESSES))}")

if __name__ == "__main__":
    main()