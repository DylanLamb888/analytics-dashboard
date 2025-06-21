"""Simple ZIP code to coordinates mapping for demo."""

# Sample ZIP code data for major US cities
ZIP_COORDINATES = {
    # California
    "94103": (37.7726, -122.4099),  # San Francisco
    "90028": (34.1016, -118.3267),  # Los Angeles
    "92101": (32.7157, -117.1611),  # San Diego
    "94108": (37.7749, -122.4194),  # San Francisco
    "90038": (34.0928, -118.3287),  # Los Angeles
    
    # New York
    "10005": (40.7074, -74.0113),   # New York
    "10010": (40.7389, -73.9876),   # New York
    "10022": (40.7589, -73.9680),   # New York
    "10017": (40.7519, -73.9777),   # New York
    "10170": (40.7527, -73.9772),   # New York
    
    # Texas
    "78701": (30.2672, -97.7431),   # Austin
    "77002": (29.7604, -95.3698),   # Houston
    "75201": (32.7767, -96.7970),   # Dallas
    "75202": (32.7831, -96.8067),   # Dallas
    
    # Florida
    "33139": (25.7817, -80.1309),   # Miami Beach
    "33140": (25.8103, -80.1269),   # Miami Beach
    "33132": (25.7739, -80.1973),   # Miami
    "32801": (28.5383, -81.3792),   # Orlando
    "32250": (30.2735, -81.4388),   # Jacksonville
    
    # Illinois
    "60601": (41.8781, -87.6298),   # Chicago
    "60606": (41.8786, -87.6359),   # Chicago
    "60654": (41.8949, -87.6341),   # Chicago
    "60611": (41.8969, -87.6235),   # Chicago
    
    # Washington
    "98101": (47.6062, -122.3321),  # Seattle
    "98104": (47.6038, -122.3262),  # Seattle
    "98122": (47.6138, -122.3037),  # Seattle
    
    # Massachusetts
    "02110": (42.3601, -71.0589),   # Boston
    "02109": (42.3663, -71.0544),   # Boston
    "02210": (42.3467, -71.0392),   # Boston
    "02116": (42.3496, -71.0764),   # Boston
    
    # Colorado
    "80218": (39.7392, -104.9847),  # Denver
    "80205": (39.7544, -104.9664),  # Denver
    "80203": (39.7312, -104.9826),  # Denver
    "80302": (40.0150, -105.2705),  # Boulder
    
    # Georgia
    "30303": (33.7490, -84.3880),   # Atlanta
    "30308": (33.7709, -84.3831),   # Atlanta
    
    # Arizona
    "85004": (33.4484, -112.0740),  # Phoenix
    "85281": (33.4255, -111.9400),  # Tempe
}

def get_coordinates_for_zip(zip_code: str):
    """Get coordinates for a ZIP code."""
    return ZIP_COORDINATES.get(zip_code, (None, None))