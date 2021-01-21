# -*- coding: utf-8 -*-

from django.urls import path

from robocjk.api.views import (
    ping, auth_token, auth_refresh_token,
    user_list, user_me,
    project_list, project_get, project_create, project_delete,
    font_list, font_get, font_create, font_update, font_delete,
    glyphs_composition_get, glyphs_composition_update,
    glif_list, glif_lock, glif_unlock,
    atomic_element_list, atomic_element_get, atomic_element_create,
    atomic_element_update, atomic_element_update_status, atomic_element_delete,
    atomic_element_lock, atomic_element_unlock,
    atomic_element_layer_create, atomic_element_layer_rename,
    atomic_element_layer_update, atomic_element_layer_delete,
    deep_component_list, deep_component_get, deep_component_create,
    deep_component_update, deep_component_update_status, deep_component_delete,
    deep_component_lock, deep_component_unlock,
    character_glyph_list, character_glyph_get, character_glyph_create,
    character_glyph_update, character_glyph_update_status, character_glyph_delete,
    character_glyph_lock, character_glyph_unlock,
    character_glyph_layer_create, character_glyph_layer_rename,
    character_glyph_layer_update, character_glyph_layer_delete, )


urlpatterns = [

    # Ping
    path('api/ping/', ping, name='ping'),

    # Auth (jwt token)
    path('api/auth/token/', auth_token, name='auth_token'),
    path('api/auth/token-refresh/', auth_refresh_token, name='auth_token_refresh'),

    # Users
    path('api/user/list/', user_list, name='user_list'),
    # path('api/user/get/', user_get, name='user_get'),
    path('api/user/me/', user_me, name='user_me'),
    # path('api/user/create/', user_create, name='user_create'),
    # path('api/user/update/', user_update, name='user_update'),
    # path('api/user/delete/', user_delete, name='user_delete'),

    # Project
    path('api/project/list/', project_list, name='project_list'),
    path('api/project/get/', project_get, name='project_get'),
    path('api/project/create/', project_create, name='project_create'),
    # path('api/project/rename/', project_rename, name='project_rename'),
    # path('api/project/update/', project_update, name='project_update'),
    path('api/project/delete/', project_delete, name='project_delete'),

    # Font
    path('api/font/list/', font_list, name='font_list'),
    path('api/font/get/', font_get, name='font_get'),
    path('api/font/create/', font_create, name='font_create'),
    path('api/font/update/', font_update, name='font_update'),
    # path('api/font/rename/', font_rename, name='font_rename'),
    path('api/font/delete/', font_delete, name='font_delete'),

    # Gliphs Composition
    path('api/glyphs-composition/get/', glyphs_composition_get, name='glyphs_composition_get'),
    path('api/glyphs-composition/update/', glyphs_composition_update, name='glyphs_composition_update'),

    # All glif (Atomic Element + Deep Component + Character Glyph)
    path('api/glif/list/', glif_list, name='glif_list'),
    path('api/glif/lock/', glif_lock, name='glif_lock'),
    path('api/glif/unlock/', glif_unlock, name='glif_unlock'),

    # Atomic Element
    path('api/atomic-element/list/', atomic_element_list, name='atomic_element_list'),
    path('api/atomic-element/get/', atomic_element_get, name='atomic_element_get'),
    path('api/atomic-element/create/', atomic_element_create, name='atomic_element_create'),
    path('api/atomic-element/update/', atomic_element_update, name='atomic_element_update'),
    path('api/atomic-element/update-status/', atomic_element_update_status, name='atomic_element_update_status'),
    path('api/atomic-element/delete/', atomic_element_delete, name='atomic_element_delete'),
    path('api/atomic-element/lock/', atomic_element_lock, name='atomic_element_lock'),
    path('api/atomic-element/unlock/', atomic_element_unlock, name='atomic_element_unlock'),
    path('api/atomic-element/layer/create/', atomic_element_layer_create, name='atomic_element_layer_create'),
    path('api/atomic-element/layer/rename/', atomic_element_layer_rename, name='atomic_element_layer_rename'),
    path('api/atomic-element/layer/update/', atomic_element_layer_update, name='atomic_element_layer_update'),
    path('api/atomic-element/layer/delete/', atomic_element_layer_delete, name='atomic_element_layer_delete'),

    # Deep Component
    path('api/deep-component/list/', deep_component_list, name='deep_component_list'),
    path('api/deep-component/get/', deep_component_get, name='deep_component_get'),
    path('api/deep-component/create/', deep_component_create, name='deep_component_create'),
    path('api/deep-component/update/', deep_component_update, name='deep_component_update'),
    path('api/deep-component/update-status/', deep_component_update_status, name='deep_component_update_status'),
    path('api/deep-component/delete/', deep_component_delete, name='deep_component_delete'),
    path('api/deep-component/lock/', deep_component_lock, name='deep_component_lock'),
    path('api/deep-component/unlock/', deep_component_unlock, name='deep_component_unlock'),

    # Character Glyph
    path('api/character-glyph/list/', character_glyph_list, name='character_glyph_list'),
    path('api/character-glyph/get/', character_glyph_get, name='character_glyph_get'),
    path('api/character-glyph/create/', character_glyph_create, name='character_glyph_create'),
    path('api/character-glyph/update/', character_glyph_update, name='character_glyph_update'),
    path('api/character-glyph/update-status/', character_glyph_update_status, name='character_glyph_update_status'),
    path('api/character-glyph/delete/', character_glyph_delete, name='character_glyph_delete'),
    path('api/character-glyph/lock/', character_glyph_lock, name='character_glyph_lock'),
    path('api/character-glyph/unlock/', character_glyph_unlock, name='character_glyph_unlock'),
    path('api/character-glyph/layer/create/', character_glyph_layer_create, name='character_glyph_layer_create'),
    path('api/character-glyph/layer/rename/', character_glyph_layer_rename, name='character_glyph_layer_rename'),
    path('api/character-glyph/layer/update/', character_glyph_layer_update, name='character_glyph_layer_update'),
    path('api/character-glyph/layer/delete/', character_glyph_layer_delete, name='character_glyph_layer_delete'),
]
