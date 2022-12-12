from robocjk.api.auth import decode_auth_token, encode_auth_token


def encode_lock_key(user, glif, date):
    assert user
    assert glif
    assert date
    key = encode_auth_token({
        "user_id": user.id,
        "glif_type": f"{glif.__class__.__name__}",
        "glif_id": glif.id,
        "date": date.isoformat(),
    })
    return key


def decode_lock_key(key):
    assert key
    data = decode_auth_token(key)
    if not data:
        raise ValueError(f"Unable to decode key: '{key}'.")
    return data
