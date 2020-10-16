# -*- coding: utf-8 -*-

from benedict import benedict

from django.conf import settings
from django.urls import reverse

import requests


class Client(object):


    @staticmethod
    def _if_int(value):
        return value if isinstance(value, int) else None


    @staticmethod
    def _if_str(value):
        return value if isinstance(value, str) else None


    def __init__(self, username, password):
        # TODO: dynamic dev/prod host
        self._host = 'http://164.90.229.235'
        self._username = username
        self._password = password
        self._auth_token = None


    def _api_call(self, view_name, params=None):
        # get api absolute url
        url = _api_url(view_name)
        # clean request post data (remove empty entries)
        data = benedict(params or {})
        data.clean()
        # build request headers
        headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Bearer {}'.format(self._auth_token)
        headers['Cache-Control'] = 'no-cache'
        # request options
        options = {
            'data': data,
            'headers': headers,
            'verify': False, # TODO
        }
        # send post request
        response = requests.post(url, **options)
        if response.status_code == 401:
            # unauthorized - request a new auth token
            self.auth_token()
            return self._api_call(view_name, params)
        # read response json data and return dict
        response_data = benedict(response.json())
        return response_data


    def _api_url(self, view_name):
        url = reverse(view_name)
        abs_url = '{}{}'.format(self._host, url)
        return abs_url


    def auth_token(self):
        params = {
            'username': self._username,
            'password': self._password,
        }
        response_data = self._api_call('auth_token', params)
        self._auth_token = response_data.get('data.auth_token', None)
        return response_data


    def auth_refresh_token(self, token):
        # TODO
        raise NotImplementedError()


    def project_list(self):
        return self._api_call('project_list')


    def project_get(self, project_uid):
        params = {
            'project_uid': project_uid,
        }
        return self._api_call('project_get', params)


    def font_list(self):
        return self._api_call('font_list')


    def font_get(self, font_uid):
        params = {
            'font_uid': font_uid,
        }
        return self._api_call('font_get', params)


    def font_update(self, font_uid, fontlib):
        params = {
            'font_uid': font_uid,
            'fontlib': json.dumps(fontlib) if isinstance(fontlib, dict) else fontlib,
        }
        return self._api_call('font_update', params)


    def glif_list(self, font_uid, is_locked_by_current_user=None, is_locked=None, is_empty=None, has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        params = {
            'font_uid': font_uid,
            'is_locked_by_current_user':, is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('glif_list', params)


    def atomic_element_list(self, font_uid, is_locked_by_current_user=None, is_locked=None, is_empty=None, has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        params = {
            'font_uid': font_uid,
            'is_locked_by_current_user': is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('atomic_element_list', params)


    def atomic_element_get(self, font_uid, atomic_element_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_get', params)


    def atomic_element_create(self, font_uid, atomic_element_data):
        params = {
            'font_uid': font_uid,
            'data': atomic_element_data,
        }
        return self._api_call('atomic_element_create', params)


    def atomic_element_update(self, font_uid, atomic_element_id, atomic_element_data):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
            'data': atomic_element_data,
        }
        return self._api_call('atomic_element_update', params)


    def atomic_element_update_status(self, font_uid, atomic_element_id, atomic_element_status):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
            'status': atomic_element_status,
        }
        return self._api_call('atomic_element_update_status', params)


    def atomic_element_delete(self, font_uid, atomic_element_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_delete', params)


    def atomic_element_lock(self, font_uid, atomic_element_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_lock', params)


    def atomic_element_unlock(self, font_uid, atomic_element_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_unlock', params)


    def atomic_element_layer_create(self, font_uid, atomic_element_id, layer_name, layer_data):
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'group_name': layer_name,
            'data': layer_data,
        }
        return self._api_call('atomic_element_layer_create', params)


    def atomic_element_layer_rename(self, font_uid, atomic_element_id, layer_id, layer_new_name):
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'new_group_name': layer_new_name,
        }
        return self._api_call('atomic_element_layer_rename', params)


    def atomic_element_layer_update(self, font_uid, atomic_element_id, layer_id, layer_data):
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'data': layer_data,
        }
        return self._api_call('atomic_element_layer_update', params)


    def atomic_element_layer_delete(self, font_uid, atomic_element_id, layer_id):
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
        }
        return self._api_call('atomic_element_layer_delete', params)


    def deep_component_list(self, font_uid, is_locked_by_current_user=None, is_locked=None, is_empty=None, has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        params = {
            'font_uid': font_uid,
            'is_locked_by_current_user': is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('deep_component_list', params)


    def deep_component_get(self, font_uid, deep_component_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_get', params)


    def deep_component_create(self, font_uid, deep_component_data):
        params = {
            'font_uid': font_uid,
            'data': deep_component_data,
        }
        return self._api_call('deep_component_create', params)


    def deep_component_update(self, font_uid, deep_component_id, deep_component_data):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
            'data': deep_component_data,
        }
        return self._api_call('deep_component_update', params)


    def deep_component_update_status(self, font_uid, deep_component_id, deep_component_status):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
            'status': deep_component_status,
        }
        return self._api_call('deep_component_update_status', params)


    def deep_component_delete(self, font_uid, deep_component_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_delete', params)


    def deep_component_lock(self, font_uid, deep_component_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_lock', params)


    def deep_component_unlock(self, font_uid, deep_component_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_unlock', params)


    def character_glyph_list(self, font_uid, is_locked_by_current_user=None, is_locked=None, is_empty=None, has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        params = {
            'font_uid': font_uid,
            'is_locked_by_current_user': is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('character_glyph_list', params)


    def character_glyph_get(self, font_uid, character_glyph_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_get', params)


    def character_glyph_create(self, font_uid, data):
        params = {
            'font_uid': font_uid,
            'data': character_glyph_data,
        }
        return self._api_call('character_glyph_create', params)


    def character_glyph_update(self, font_uid, character_glyph_id, character_glyph_data):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
            'data': character_glyph_data,
        }
        return self._api_call('character_glyph_update', params)


    def character_glyph_update_status(self, font_uid, character_glyph_id, character_glyph_status):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
            'status': character_glyph_status,
        }
        return self._api_call('character_glyph_update_status', params)


    def character_glyph_delete(self, font_uid, character_glyph_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_delete', params)


    def character_glyph_lock(self, font_uid, character_glyph_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_lock', params)


    def character_glyph_unlock(self, font_uid, character_glyph_id):
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_unlock', params)


    def character_glyph_layer_create(self, font_uid, character_glyph_id, layer_name, layer_data):
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'group_name': layer_name,
            'data': layer_data,
        }
        return self._api_call('character_glyph_layer_create', params)


    def character_glyph_layer_rename(self, font_uid, character_glyph_id, layer_id, layer_new_name):
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'new_group_name': layer_new_name,
        }
        return self._api_call('character_glyph_layer_rename', params)


    def character_glyph_layer_update(self, font_uid, character_glyph_id, layer_id, data):
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'data': layer_data,
        }
        return self._api_call('character_glyph_layer_update', params)


    def character_glyph_layer_delete(self, font_uid, character_glyph_id, layer_id):
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
        }
        return self._api_call('character_glyph_layer_delete', params)

