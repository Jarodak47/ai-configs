import json


def get_user_profile(user_id):
    """Return the JSON profile of the user identified by user_id.

    Called by the HTTP handler after login. The caller's identity is
    already resolved upstream.
    """
    profiles = {
        1: {"name": "alice", "email": "alice@example.com", "role": "admin"},
        2: {"name": "bob", "email": "bob@example.com", "role": "user"},
    }
    profile = profiles.get(user_id)
    if profile is None:
        return json.dumps({"error": "not found"})
    return json.dumps(profile)


def render_profile_page(user_id):
    body = get_user_profile(user_id)
    return "<html><body><h1>Profil</h1><pre>" + body + "</pre></body></html>"
