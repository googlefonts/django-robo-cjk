# -*- coding: utf-8 -*-

from django.urls import path

from robocjk.api.views import (
    auth_token, auth_refresh_token,
    project_list,
    font_list,
    glif_list,
    atomic_element_list, atomic_element_get,
    atomic_element_create, atomic_element_update, atomic_element_delete,
    atomic_element_lock, atomic_element_unlock,
    atomic_element_layer_create, atomic_element_layer_update, atomic_element_layer_delete,
    deep_component_list, deep_component_get,
    deep_component_create, deep_component_update, deep_component_delete,
    deep_component_lock, deep_component_unlock,
    character_glyph_list, character_glyph_get,
    character_glyph_create, character_glyph_update, character_glyph_delete,
    character_glyph_lock, character_glyph_unlock,
    character_glyph_layer_create, character_glyph_layer_update, character_glyph_layer_delete, )


urlpatterns = [

    # Auth (jwt token)
    path('auth/token/', auth_token, name='auth_token'),
    path('auth/token-refresh/', auth_refresh_token, name='auth_token_refresh'),

    # TODO: Project
    path('project/list/', project_list, name='project_list'),
    # path('project/get/', project_get, name='project_get'),
    # path('project/create/', project_create, name='project_create'),
    # path('project/update/', project_update, name='project_update'),
    # path('project/delete/', project_delete, name='project_delete'),

    # TODO: Font
    path('font/list/', font_list, name='font_list'),
    # path('font/get/', font_get, name='font_get'),
    # path('font/create/', font_create, name='font_create'),
    # path('font/update/', font_update, name='font_update'),
    # path('font/delete/', font_delete, name='font_delete'),

    # All glif (Atomic Element + Deep Component + Character Glyph)
    path('glif/list/', glif_list, name='glif_list'),

    # Atomic Element
    path('atomic-element/list/', atomic_element_list, name='atomic_element_list'),
    path('atomic-element/get/', atomic_element_get, name='atomic_element_get'),
    path('atomic-element/create/', atomic_element_create, name='atomic_element_create'),
    path('atomic-element/update/', atomic_element_update, name='atomic_element_update'),
    path('atomic-element/delete/', atomic_element_delete, name='atomic_element_delete'),
    path('atomic-element/lock/', atomic_element_lock, name='atomic_element_lock'),
    path('atomic-element/unlock/', atomic_element_unlock, name='atomic_element_unlock'),
    path('atomic-element/layer/create/', atomic_element_layer_create, name='atomic_element_layer_create'),
    path('atomic-element/layer/update/', atomic_element_layer_update, name='atomic_element_layer_update'),
    path('atomic-element/layer/delete/', atomic_element_layer_delete, name='atomic_element_layer_delete'),

    # Deep Component
    path('deep-component/list/', deep_component_list, name='deep_component_list'),
    path('deep-component/get/', deep_component_get, name='deep_component_get'),
    path('deep-component/create/', deep_component_create, name='deep_component_create'),
    path('deep-component/update/', deep_component_update, name='deep_component_update'),
    path('deep-component/delete/', deep_component_delete, name='deep_component_delete'),
    path('deep-component/lock/', deep_component_lock, name='deep_component_lock'),
    path('deep-component/unlock/', deep_component_unlock, name='deep_component_unlock'),

    # Character Glyph
    path('character-glyph/list/', character_glyph_list, name='character_glyph_list'),
    path('character-glyph/get/', character_glyph_get, name='character_glyph_get'),
    path('character-glyph/create/', character_glyph_create, name='deep_component_create'),
    path('character-glyph/update/', character_glyph_update, name='deep_component_update'),
    path('character-glyph/delete/', character_glyph_delete, name='deep_component_delete'),
    path('character-glyph/lock/', character_glyph_lock, name='deep_component_lock'),
    path('character-glyph/unlock/', character_glyph_unlock, name='deep_component_unlock'),
    path('character-glyph/layer/create/', character_glyph_layer_create, name='character_glyph_layer_create'),
    path('character-glyph/layer/update/', character_glyph_layer_update, name='character_glyph_layer_update'),
    path('character-glyph/layer/delete/', character_glyph_layer_delete, name='character_glyph_layer_delete'),
]
