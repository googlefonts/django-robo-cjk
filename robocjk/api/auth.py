# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

import datetime as dt
import jwt


def decode_auth_token(token):
    try:
        decoded = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidSignatureError:
        return None


def decode_auth_token_in_header(request):
    token = get_auth_token_in_header(request)
    if token:
        return decode_auth_token(auth_token)
    return None


def encode_auth_token(data):
    encoded = jwt.encode(
        data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return str(encoded, 'utf-8')


def generate_auth_token(expiration=None, data=None):
    exp_now = dt.datetime.utcnow()
    exp_options = expiration or { 'days':1 }
    exp_delta = dt.timedelta(**exp_options)
    data = data or {}
    data['exp'] = exp_now + exp_delta
    return encode_auth_token(data)


def get_auth_token(request, username, password, expiration=None, data=None):
    user = get_user_by_credentials(request, username, password)
    if user:
        data = data or {}
        data['user_pk'] = request.user.pk
        token = generate_auth_token(expiration, data)
        return token
    return None


def get_auth_token_in_header(request):
    header_key = settings.JWT_HEADER_KEY
    if header_key in request.META:
        header = request.META[header_key].split()
        if len(header) == 2:
            if header[0].lower() in ['bearer', 'jwt', 'token']:
               token = header[1]
               return token
    return None


def get_user_by_auth_token_in_header(request):
    token = get_auth_token_in_header(request)
    if token:
        return get_user_by_auth_token(token)
    return None


def get_user_by_auth_token(token):
    data = decode_auth_token(token)
    if not data:
        return None
    user_cls = get_user_model()
    user_pk = data['user_pk']
    try:
        user_obj = user_cls.objects.get(pk=user_pk)
        return user_obj
    except user_cls.DoesNotExist:
        return None


def get_user_by_credentials(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user:
        return user
    return None

