# -*- coding: utf-8 -*-

# from admin_auto_filters.filters import AutocompleteFilter

from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_json_widget.widgets import JSONEditorWidget

from robocjk.models import (
    Project,
    Font, FontImport,
    GlyphsComposition,
    CharacterGlyph, CharacterGlyphLayer,
    DeepComponent,
    AtomicElement, AtomicElementLayer,
    Proof, )


class FontFilter(admin.SimpleListFilter):
    title = _('Font')
    parameter_name = 'font'

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        fonts = Font.objects.select_related('project').all()
        return [(font.id, '{} / {}'.format(font.project.name, font.name)) for font in fonts]

    def queryset(self, request, queryset):
        font_id=self.value()
        if self.value():
            return queryset.filter(font_id=font_id)
        return queryset


class GlifFontFilter(admin.SimpleListFilter):
    title = _('Font')
    parameter_name = 'font'

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        fonts = Font.objects.select_related('project').all()
        return [(font.id, '{} / {}'.format(font.project.name, font.name)) for font in fonts]

    def queryset(self, request, queryset):
        font_id=self.value()
        if self.value():
            return queryset.select_related('glif').filter(glif__font_id=font_id)
        return queryset


# class GlifFilter(AutocompleteFilter):
#
#     title = _('Glif')
#     field_name = 'glif'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_select_related = ()
    list_display = ('name', 'slug', 'uid', 'hashid', 'repo_url', 'num_fonts', 'created_at', 'updated_at', 'updated_by', )
    # list_filter = ('updated_by', )
    search_fields = ('name', 'slug', 'uid', 'hashid', )
    readonly_fields = ('id', 'hashid', 'uid', 'slug', 'created_at', 'updated_at', 'updated_by', )
    fieldsets = (
        ('Identifiers', {
            'classes': ('collapse',),
            'fields': ('hashid', 'uid', )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'updated_by', )
        }),
        (None, {
            'fields': ('name', 'slug', 'repo_url', )
        }),
    )
    save_on_top = True
    show_full_result_count = False


@admin.register(FontImport)
class FontImportAdmin(admin.ModelAdmin):

    list_select_related = ()
    list_display = ('filename', 'status', 'created_at', 'updated_at', )
    list_filter = (FontFilter, 'status', )
    readonly_fields = ('id', 'status', 'created_at', 'updated_at', 'updated_by', )
    fieldsets = (
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'updated_by', )
        }),
        (None, {
            'fields': ('font', 'file', 'status', 'logs', )
        }),
    )
    save_on_top = True
    show_full_result_count = False


class FontImportInline(admin.TabularInline):

    model = FontImport
    fields = ('file', 'filename', 'status', 'created_at', 'updated_at', )
    readonly_fields = ('filename', 'status', 'created_at', 'updated_at', )
    extra = 0


@admin.register(Font)
class FontAdmin(admin.ModelAdmin):

    def info(self, font, *args, **kwargs):
        html = '<span style="white-space: nowrap;">Character Glyphs: <strong>{}</strong></span><br>'\
               '<span style="white-space: nowrap;">Deep Components: <strong>{}</strong></span><br>'\
               '<span style="white-space: nowrap;">Atomic Elements: <strong>{}</strong></span>'.format(
                    font.num_character_glyphs(),
                    font.num_deep_components(),
                    font.num_atomic_elements())
        return mark_safe(html)

    list_select_related = ()
    list_display = ('name', 'slug', 'uid', 'hashid', 'info', 'available', 'created_at', 'updated_at', 'updated_by', )
    list_filter = ('project', 'available', 'updated_by', )
    search_fields = ('name', 'slug', 'uid', 'hashid', )
    readonly_fields = ('id', 'hashid', 'uid', 'slug', 'available', 'created_at', 'updated_at', 'updated_by', )
    fieldsets = (
        ('Identifiers', {
          'classes': ('collapse',),
          'fields': ('hashid', 'uid', )
        }),
        ('Metadata', {
          'classes': ('collapse',),
          'fields': ('created_at', 'updated_at', 'updated_by', )
        }),
        (None, {
          'fields': ('project', 'name', 'slug', 'available', 'fontlib', )
        }),
    )
    inlines = [FontImportInline]
    save_on_top = True
    show_full_result_count = False
    formfield_overrides = {
        models.JSONField: {
            'widget': JSONEditorWidget(width='100%', height='350px'),
        },
    }


@admin.register(GlyphsComposition)
class GlyphsCompositionAdmin(admin.ModelAdmin):

    list_select_related = ()
    list_display = ('font', 'created_at', 'updated_at', 'updated_by', )
    list_filter = ('updated_by', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', )
    fieldsets = (
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'updated_by', )
        }),
        (None, {
            'fields': ('font', 'data', )
        }),
    )
    save_on_top = True
    show_full_result_count = False
    formfield_overrides = {
        models.JSONField: {
            'widget': JSONEditorWidget(width='100%', height='500px'),
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
            white-space: nowrap;
            '''.format(obj.status_color)
        html = '<span style="{}">{}</span>'.format(
            css, obj.get_status_display())
        return mark_safe(html)

    status_display.short_description = _('Status')
    status_display.allow_tags = True

    list_select_related = ()
    list_display = ('name', 'filename', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', 'is_locked', 'status_display', 'created_at', 'updated_at', 'updated_by', )
    list_display_links = ('name', )
    list_filter = (FontFilter, 'status', 'updated_by', 'locked_by', 'is_locked', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', )
    search_fields = ('name', 'filename', 'unicode_hex', 'components', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'name', 'filename', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )
    # raw_id_fields = ('font', )

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


class GlifLayerAdmin(admin.ModelAdmin):

    list_select_related = ()
    list_display = ('group_name', 'name', 'filename', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', 'created_at', 'updated_at', 'updated_by', )
    list_display_links = ('group_name', )
    list_filter = (GlifFontFilter, 'updated_by', 'group_name', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', )
    search_fields = ('group_name', 'name', 'filename', 'components', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'name', 'filename', 'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )
    raw_id_fields = ('glif', )
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


# @admin.register(Proof)
# class ProofAdmin(admin.ModelAdmin):
#
#     list_select_related = ()
#     list_display = ('file', 'filetype', 'created_at', 'updated_at', 'updated_by', 'user', )
#     list_filter = ('font', 'user', 'filetype', )
#     search_fields = ('file', 'filetype', )
#     readonly_fields = ('created_at', 'updated_at', 'updated_by', )
#     fieldsets = (
#         ('Metadata', {
#             'classes': ('collapse', ),
#             'fields': ('created_at', 'updated_at', 'updated_by', )
#         }),
#         (None, {
#             'fields': ('user', 'file', 'filetype', )
#         }),
#     )
#     save_on_top = True

