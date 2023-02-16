import datetime as dt

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

# from robocjk.debug import logger


def decode_auth_token(token):
    try:
        decoded = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded
    except jwt.ExpiredSignatureError:
        # logger.error('decode_auth_token -> jwt.ExpiredSignatureError')
        return None
    except jwt.InvalidSignatureError:
        # logger.error('decode_auth_token -> jwt.InvalidSignatureError')
        return None


def decode_auth_token_in_header(request):
    token = get_auth_token_in_header(request)
    if token:
        return decode_auth_token(token)
    # logger.error('decode_auth_token_in_header -> token not found')
    return None


def encode_auth_token(data):
    encoded = jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    if isinstance(encoded, str):
        return encoded
    elif isinstance(encoded, bytes):
        return str(encoded, "utf-8")
    else:
        return None


def generate_auth_token(expiration=None, data=None):
    exp_now = dt.datetime.utcnow()
    exp_options = expiration or {"days": 1}
    exp_delta = dt.timedelta(**exp_options)
    data = data.copy() if data else {}
    data["exp"] = exp_now + exp_delta
    return encode_auth_token(data)


def get_auth_token(request, username, password, expiration=None, data=None):
    user = get_user_by_credentials(request, username, password)
    if user:
        data = data or {}
        data["user_pk"] = user.pk
        token = generate_auth_token(expiration, data)
        return token
    # logger.error('get_auth_token -> user not found')
    return None


def get_auth_token_in_header(request):
    for header_key in ["Authorization", "HTTP_AUTHORIZATION"]:
        if header_key in request.META:
            header = request.META[header_key].split()
            if len(header) == 2:
                if header[0].lower() in ["bearer", "jwt", "token"]:
                    token = header[1]
                    return token
    # logger.error('get_auth_token_in_header -> token not found')
    return None


def get_user_by_auth_token_in_header(request):
    token = get_auth_token_in_header(request)
    if token:
        return get_user_by_auth_token(token)
    # logger.error('get_user_by_auth_token_in_header -> token not found')
    return None


def get_user_by_auth_token(token):
    data = decode_auth_token(token)
    if not data:
        # logger.error('get_user_by_auth_token -> token payload not found')
        return None
    user_cls = get_user_model()
    user_pk = data["user_pk"]
    try:
        user_obj = user_cls.objects.get(pk=user_pk)
        return user_obj
    except user_cls.DoesNotExist:
        # logger.error('get_user_by_auth_token -> user not found')
        return None


def get_user_by_credentials(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user:
        return user
    # logger.error('get_user_by_credentials -> user not found')
    return None
