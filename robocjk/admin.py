# -*- coding: utf-8 -*-

from admin_auto_filters.filters import AutocompleteFilter

from copy import deepcopy

from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_json_widget.widgets import JSONEditorWidget

from robocjk.models import (
    Project, Font, CharacterGlyph, CharacterGlyphLayer, DeepComponent,
    AtomicElement, AtomicElementLayer, Proof, )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug', 'uid', 'hashid', 'repo_url', 'num_fonts', 'created_at', 'updated_at', )
    search_fields = ('name', 'slug', 'uid', 'hashid', )
    readonly_fields = ('id', 'hashid', 'uid', 'slug', 'created_at', 'updated_at', )
    fieldsets = (
      ('Identifiers', {
          'classes': ('collapse',),
          'fields': ('hashid', 'uid', )
      }),
      ('Metadata', {
          'classes': ('collapse',),
          'fields': ('created_at', 'updated_at', )
      }),
      (None, {
          'fields': ('name', 'slug', 'repo_url', )
      }),
    )
    save_on_top = True


@admin.register(Font)
class FontAdmin(admin.ModelAdmin):

    def info(self, font, *args, **kwargs):
        html = 'Character Glyphs: <strong>{}</strong><br>'\
               'Deep Components: <strong>{}</strong><br>'\
               'Atomic Elements: <strong>{}</strong>'.format(
                    font.num_character_glyphs(),
                    font.num_deep_components(),
                    font.num_atomic_elements())
        return mark_safe(html)

    list_display = ('name', 'slug', 'uid', 'hashid', 'info', 'available', 'created_at', 'updated_at', )
    list_filter = ('project', 'available', )
    search_fields = ('name', 'slug', 'uid', 'hashid', )
    readonly_fields = ('id', 'hashid', 'uid', 'slug', 'available', 'created_at', 'updated_at', )
    fieldsets = (
      ('Identifiers', {
          'classes': ('collapse',),
          'fields': ('hashid', 'uid', )
      }),
      ('Metadata', {
          'classes': ('collapse',),
          'fields': ('created_at', 'updated_at', )
      }),
      (None, {
          'fields': ('project', 'name', 'slug', 'available', 'fontlib', ) # 'glyphs_composition',
      }),
    )
    save_on_top = True

    formfield_overrides = {
        models.JSONField: {
            'widget': JSONEditorWidget(width='100%', height='350px'),
        },
    }


class GlifAdmin(admin.ModelAdmin):

    def status_display(self, obj):
        css = '''
            color: #FFFFFF;
            background-color: {};
            text-transform: uppercase;
            font-size: 80%;
            padding: 3px 5px 2px;
            border-radius: 3px;
            line-height: 1.0;
            '''.format(obj.status_color)
        html = '<span style="{}">{}</span>'.format(
            css, obj.get_status_display())
        return mark_safe(html)

    status_display.short_description = _('Status')
    status_display.allow_tags = True

    list_display = ('name', 'filename', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', 'is_locked', 'status_display', 'created_at', 'updated_at', 'updated_by', )
    list_display_links = ('name', )
    list_filter = ('font__project', 'font', 'status', 'updated_by', 'locked_by', 'is_locked', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', )
    search_fields = ('name', 'filename', 'unicode_hex', 'components', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'name', 'filename', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )

    def get_fieldsets(self, request, obj=None):
        return (
            ('Metadata', {
                'classes': ('collapse', ),
                'fields': ('created_at', 'updated_at', 'updated_by', 'is_locked', 'locked_by', 'locked_at', )
            }),
            (None, {
                'fields': ('font', 'status', 'data', 'name', 'filename', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )
            }),
        )

    save_on_top = True
    show_full_result_count = False


class GlifFilter(AutocompleteFilter):

    title = _('Glif')
    field_name = 'glif'


class GlifLayerAdmin(admin.ModelAdmin):

    list_display = ('group_name', 'name', 'filename', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', 'created_at', 'updated_at', 'updated_by', )
    list_display_links = ('group_name', )
    list_filter = (GlifFilter, 'updated_by', 'group_name', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', )
    search_fields = ('group_name', 'name', 'filename', 'components', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'name', 'filename', 'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )
    fieldsets = (
        ('Metadata', {
            'classes': ('collapse', ),
            'fields': ('created_at', 'updated_at', 'updated_by', )
        }),
        (None, {
            'fields': ('glif', 'group_name', 'data', 'name', 'filename', 'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )
        }),
    )
    save_on_top = True
    show_full_result_count = False


class GlifLayerInline(admin.TabularInline):

    fields = ('group_name', 'data', 'name', 'filename', )
    readonly_fields = ('name', 'filename', )
    extra = 0


class CharacterGlyphLayerInline(GlifLayerInline):

    model = CharacterGlyphLayer


@admin.register(CharacterGlyph)
class CharacterGlyphAdmin(GlifAdmin):

    def get_fieldsets(self, request, obj=None):
        f = super(CharacterGlyphAdmin, self).get_fieldsets(request, obj)
        f[-1][-1]['fields'] += ('deep_components', )
        return f

    filter_horizontal = ['deep_components']
    inlines = [CharacterGlyphLayerInline]


@admin.register(CharacterGlyphLayer)
class CharacterGlyphLayerAdmin(GlifLayerAdmin):

    pass


@admin.register(DeepComponent)
class DeepComponentAdmin(GlifAdmin):

    def get_fieldsets(self, request, obj=None):
        f = super(DeepComponentAdmin, self).get_fieldsets(request, obj)
        f[-1][-1]['fields'] += ('atomic_elements', )
        return f

    filter_horizontal = ['atomic_elements']


class AtomicElementLayerInline(GlifLayerInline):

    model = AtomicElementLayer


@admin.register(AtomicElement)
class AtomicElementAdmin(GlifAdmin):

    inlines = [AtomicElementLayerInline]


@admin.register(AtomicElementLayer)
class AtomicElementLayerAdmin(GlifLayerAdmin):

    pass


@admin.register(Proof)
class ProofAdmin(admin.ModelAdmin):

    list_display = ('file', 'filetype', 'created_at', 'updated_at', 'user', )
    list_filter = ('font', 'user', 'filetype', )
    search_fields = ('file', 'filetype', )
    readonly_fields = ('created_at', 'updated_at', )
    fieldsets = (
        ('Metadata', {
            'classes': ('collapse', ),
            'fields': ('created_at', 'updated_at', )
        }),
        (None, {
            'fields': ('user', 'file', 'filetype', )
        }),
    )
    save_on_top = True

