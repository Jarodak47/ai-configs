from app import build_query, find_user

assert "alice" in build_query("alice")
assert find_user("alice") == []
print("OK")
