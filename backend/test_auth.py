"""Quick test script to verify authentication."""

import sys
sys.path.append('..')
from backend.core.security import authenticate_user, verify_password, get_password_hash

# Test the demo users
print("Testing authentication...")
print()

# Test admin login
admin_user = authenticate_user("admin@example.com", "admin123")
if admin_user:
    print("✅ Admin login successful:", admin_user["email"])
else:
    print("❌ Admin login failed")

# Test viewer login
viewer_user = authenticate_user("viewer@example.com", "viewer123")
if viewer_user:
    print("✅ Viewer login successful:", viewer_user["email"])
else:
    print("❌ Viewer login failed")

# Test wrong password
wrong_user = authenticate_user("viewer@example.com", "wrongpassword")
if not wrong_user:
    print("✅ Wrong password correctly rejected")
else:
    print("❌ Wrong password incorrectly accepted")

# Show password hashes for debugging
print("\nPassword hashes:")
print(f"admin123: {get_password_hash('admin123')}")
print(f"viewer123: {get_password_hash('viewer123')}")