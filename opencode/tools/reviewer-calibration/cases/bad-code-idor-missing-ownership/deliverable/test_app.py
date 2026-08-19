import json
from app import get_user_profile

assert "alice" in get_user_profile(1)
assert "bob" in get_user_profile(2)
assert json.loads(get_user_profile(999)) == {"error": "not found"}
print("OK")
