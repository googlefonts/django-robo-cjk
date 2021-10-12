# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_json_widget.widgets import JSONEditorWidget
from rangefilter.filters import DateTimeRangeFilter

from robocjk.models import (
    Project,
    Font, FontImport,
    GlyphsComposition,
    CharacterGlyph, CharacterGlyphLayer,
    DeepComponent,
    AtomicElement, AtomicElementLayer,
    Proof, StatusModel,
)
from robocjk.utils import unicode_to_char


admin.site.unregister(User)


@admin.register(User)
class CustomizedUserAdmin(UserAdmin):

    """
    https://github.com/django/django/blob/master/django/contrib/auth/admin.py
    """

    save_on_top = True

    def _is_administrator(self, request):
        user = request.user
        return user.is_superuser or user.groups.filter(name__iexact='administrators').exists()

    def get_queryset(self, request):
        qs = super(CustomizedUserAdmin, self).get_queryset(request)
        if self._is_administrator(request):
            return qs
        # only for who is not administrator (designers)
        # show only their own record in the changelist
        return qs.filter(pk=request.user.pk)

    def get_fieldsets(self, request, obj=None):
        f = super(CustomizedUserAdmin, self).get_fieldsets(request, obj=obj)
        if self._is_administrator(request):
            return f
        # only for who is not administrator (designers)
        # don't show permissions and groups fieldset
        return (f[0], f[1], f[3], )

    def get_readonly_fields(self, request, obj=None):
        f = super(CustomizedUserAdmin, self).get_readonly_fields(request, obj=obj)
        if self._is_administrator(request):
            return f
        # only for who is not administrator (designers)
        # allow only 'first_name', 'last_name', 'email' and 'password' modification
        # return ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', )
        return ('username', 'last_login', 'date_joined', )

    def get_list_filter(self, request):
        f = super(CustomizedUserAdmin, self).get_list_filter(request)
        if self._is_administrator(request):
            return f
        return ()


class FontFilter(admin.SimpleListFilter):

    title = _('Font')
    parameter_name = 'font'

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        fonts = Font.objects.select_related('project').order_by('project__name', 'name').all()
        return [(font.id, '{} / {}'.format(font.project.name, font.name)) for font in fonts]

    def queryset(self, request, queryset):
        font_id=self.value()
        if font_id:
            return queryset.filter(font_id=font_id)
        return queryset


class GlifFontFilter(FontFilter):

    def queryset(self, request, queryset):
        font_id=self.value()
        if self.value():
            return queryset.select_related('glif').filter(glif__font_id=font_id)
        return queryset


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_select_related = ('updated_by', )
    list_display = ('name', 'slug', 'uid', 'hashid', 'repo_url', 'num_fonts', 'num_designers', 'created_at', 'updated_at', 'updated_by', 'export_enabled', 'export_running', 'export_started_at', 'export_completed_at', )
    # list_filter = ('updated_by', )
    list_filter = ('export_enabled', 'export_running', )
    search_fields = ('name', 'slug', 'uid', 'hashid', )
    readonly_fields = ('id', 'hashid', 'uid', 'slug', 'created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
    fieldsets = (
        ('Identifiers', {
            'classes': ('collapse',),
            'fields': ('hashid', 'uid', )
        }),
        ('Export', {
            'classes': ('collapse',),
            'fields': ('export_enabled', 'export_running', 'export_started_at', 'export_completed_at', )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
        }),
        (None, {
            'fields': ('name', 'slug', 'repo_url', 'designers', )
        }),
    )
    filter_horizontal = ('designers', )
    save_on_top = True
    show_full_result_count = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            num_fonts=Count('fonts', distinct=True),
            num_designers=Count('designers', distinct=True))
        return qs


@admin.register(FontImport)
class FontImportAdmin(admin.ModelAdmin):

    list_select_related = ()
    list_display = ('filename', 'status', 'created_at', 'updated_at', )
    list_filter = (FontFilter, 'status', )
    readonly_fields = ('id', 'created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
    fieldsets = (
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
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

    def progress(self, font, *args, **kwargs):

        tot = 0
        tot_wip = 0
        tot_checking_1 = 0
        tot_checking_2 = 0
        tot_checking_3 = 0
        tot_done = 0

        for cls in [CharacterGlyph, DeepComponent, AtomicElement]:
            manager = cls.objects
            tot += manager.filter(font=font).count()
            tot_wip += manager.filter(font=font, status=cls.STATUS_WIP).count()
            tot_checking_1 += manager.filter(font=font, status=cls.STATUS_CHECKING_1).count()
            tot_checking_2 += manager.filter(font=font, status=cls.STATUS_CHECKING_2).count()
            tot_checking_3 += manager.filter(font=font, status=cls.STATUS_CHECKING_3).count()
            tot_done += manager.filter(font=font, status=cls.STATUS_DONE).count()

        perc_wip = 0
        perc_checking_1 = 0
        perc_checking_2 = 0
        perc_checking_3 = 0
        perc_done = 0

        if tot > 0:
            perc_wip = ((tot_wip * 100) / tot)
            perc_checking_1 = ((tot_checking_1 * 100) / tot)
            perc_checking_2 = ((tot_checking_2 * 100) / tot)
            perc_checking_3 = ((tot_checking_3 * 100) / tot)
            perc_done = ((tot_done * 100) / tot)

        color_wip = StatusModel.STATUS_COLOR_WIP
        color_checking_1 = StatusModel.STATUS_COLOR_CHECKING_1
        color_checking_2 = StatusModel.STATUS_COLOR_CHECKING_2
        color_checking_3 = StatusModel.STATUS_COLOR_CHECKING_3
        color_done = StatusModel.STATUS_COLOR_DONE

        title_wip = '{}: {}%'.format(
            StatusModel.STATUS_DISPLAY_WIP,
            round(perc_wip))
        title_checking_1 = '{}: {}%'.format(
            StatusModel.STATUS_DISPLAY_CHECKING_1,
            round(perc_checking_1))
        title_checking_2 = '{}: {}%'.format(
            StatusModel.STATUS_DISPLAY_CHECKING_2,
            round(perc_checking_2))
        title_checking_3 = '{}: {}%'.format(
            StatusModel.STATUS_DISPLAY_CHECKING_3,
            round(perc_checking_3))
        title_done = '{}: {}%'.format(
            StatusModel.STATUS_DISPLAY_DONE,
            round(perc_done))

        html = """
            <div style="display: block; width: 100%; min-width: 150px; height: 15px; position: relative; background-color: rgba(0,0,0,0.1);">
                <span style="display: inline-block; float: left; width: {}%; height: 100%; background-color: {};" title="{}"></span>
                <span style="display: inline-block; float: left; width: {}%; height: 100%; background-color: {};" title="{}"></span>
                <span style="display: inline-block; float: left; width: {}%; height: 100%; background-color: {};" title="{}"></span>
                <span style="display: inline-block; float: left; width: {}%; height: 100%; background-color: {};" title="{}"></span>
                <span style="display: inline-block; float: left; width: {}%; height: 100%; background-color: {};" title="{}"></span>
            </div>
            """.format(
                perc_wip, color_wip, title_wip,
                perc_checking_1, color_checking_1, title_checking_1,
                perc_checking_2, color_checking_2, title_checking_2,
                perc_checking_3, color_checking_3, title_checking_3,
                perc_done, color_done, title_done,
            )
        return mark_safe(html)

    list_select_related = ('project', 'updated_by', ) #'info', 'progress',
    list_display = ('project', 'name', 'uid', 'hashid', 'info', 'available', 'created_at', 'updated_at', 'updated_by', 'export_enabled', 'export_running', 'export_started_at', 'export_completed_at', )
    list_display_links = ('name', )
    list_filter = ('project', 'available', 'updated_by', 'export_enabled', 'export_running', )
    search_fields = ('name', 'slug', 'uid', 'hashid', )
    readonly_fields = ('id', 'hashid', 'uid', 'slug', 'available', 'created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
    fieldsets = (
        ('Identifiers', {
          'classes': ('collapse',),
          'fields': ('hashid', 'uid', )
        }),
        ('Export', {
            'classes': ('collapse',),
            'fields': ('export_running', 'export_started_at', 'export_completed_at', )
        }),
        ('Metadata', {
          'classes': ('collapse',),
          'fields': ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
        }),
        (None, {
          'fields': ('project', 'name', 'slug', 'available', 'fontlib', 'features', 'designspace', )
        }),
    )
    inlines = [FontImportInline]
    save_on_top = True
    show_full_result_count = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
#         qs = qs.annotate(
#             # num_character_glyphs=Count('character_glyphs', distinct=True),
#             num_deep_components=Count('deep_components', distinct=True),
#             num_atomic_elements=Count('atomic_elements', distinct=True))
        return qs

    formfield_overrides = {
        models.JSONField: {
            'widget': JSONEditorWidget(width='100%', height='350px'),
        },
    }


@admin.register(GlyphsComposition)
class GlyphsCompositionAdmin(admin.ModelAdmin):

    list_select_related = ('font', 'updated_by', )
    list_display = ('font', 'created_at', 'updated_at', 'updated_by', )
    list_filter = (FontFilter, 'updated_by', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
    fieldsets = (
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
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

    list_select_related = ('updated_by', )
    list_display = ('name', 'filename', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', 'is_locked', 'status_display', 'created_at', 'updated_at', 'updated_by', )
    list_display_links = ('name', )
    list_filter = (FontFilter, 'status', ('status_changed_at', DateTimeRangeFilter, ), 'previous_status', 'updated_by', 'locked_by', 'is_locked', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', )
    search_fields = ('name', 'filename', 'unicode_hex', 'components', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', 'name', 'filename', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )
    # raw_id_fields = ('font', )

    def get_fieldsets(self, request, obj=None):
        return (
            ('Metadata', {
                'classes': ('collapse', ),
                'fields': ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', ),
            }),
            ('Locking', {
                'classes': ('collapse', ),
                'fields': ('is_locked', 'locked_by', 'locked_at', ),
            }),
            ('Status', {
                'classes': ('collapse', ),
                'fields': ('status', 'status_changed_at', 'previous_status', ),
            }),
            (None, {
                'fields': ('font', 'data', 'name', 'filename', 'is_empty', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'components', ),
            }),
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.defer('data')
        return qs

    save_on_top = True
    show_full_result_count = False


class GlifLayerAdmin(admin.ModelAdmin):

    list_select_related = ('updated_by', )
    list_display = ('group_name', 'name', 'filename', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', 'created_at', 'updated_at', 'updated_by', )
    list_display_links = ('group_name', )
    list_filter = (GlifFontFilter, 'updated_by', 'group_name', 'has_unicode', 'has_variation_axis', 'has_outlines', 'has_components', 'is_empty', )
    search_fields = ('group_name', 'name', 'filename', 'components', )
    readonly_fields = ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', 'name', 'filename', 'is_empty', 'has_variation_axis', 'has_outlines', 'has_components', 'components', )
    raw_id_fields = ('glif', )
    fieldsets = (
        ('Metadata', {
            'classes': ('collapse', ),
            'fields': ('created_at', 'updated_at', 'updated_by', 'editors', 'editors_history', )
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

    def character(self, obj):
        return unicode_to_char(obj.unicode_hex) if obj.unicode_hex else ''

    def get_list_display(self, request):
        l = super(CharacterGlyphAdmin, self).get_list_display(request)
        return ('character', ) + l

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

