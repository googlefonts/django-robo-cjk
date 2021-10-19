# -*- coding: utf-8 -*-

from django.http import HttpResponse

import datetime
import unicodecsv


def export_as_csv(
    description='Export selected objects as CSV file',
    fields=None, exclude=None, header=True, filename=None, date=True, time=True):

    """
    This function returns an export csv action.

    Source: https://gist.github.com/mgerring/3645889
    Usage: actions = [export_as_csv('CSV Export', fields=['firstname', 'lastname', 'email'])]
    """

    def _export_as_csv(modeladmin, request, queryset):

        opts = modeladmin.model._meta

        model_name = str(opts).split('.')[-1]
        filename_auto = filename if filename else model_name

        now = datetime.datetime.now()
        if date:
            filename_auto += '-{date:%Y%m%d}'.format(date=now)
        if time:
            filename_auto += '-{hour:%H%M%S}'.format(hour=now)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % (filename_auto, )

        field_names = None
        field_names_display = None

        if fields:
            if all(isinstance(val, tuple) for val in fields):
                if exclude:
                    field_names = [val[1] for val in fields if not val[1] in exclude]
                    field_names_display = [val[0] for val in fields if not val[1] in exclude]
                else:
                    field_names = [val[1] for val in fields]
                    field_names_display = [val[0] for val in fields]
            else:
                field_names = fields
                if exclude:
                    field_names = [n for n in field_names if not n in exclude]
                field_names_display = field_names
        else:
            # all fields - exclude fields
            field_names = [f.name for f in opts.fields]
            if exclude:
                field_names = [n for n in field_names if not n in exclude]
            field_names_display = field_names_display

        csv = unicodecsv.writer(response, encoding='utf-8')

        if header:
            row = [n for n in field_names_display]
            csv.writerow(row)

        for obj in queryset:
            obj_attrs = [getattr(obj, f, '') if f else '' for f in field_names]
            row = [a() if callable(a) else a for a in obj_attrs]
            csv.writerow(row)

        return response

    _export_as_csv.short_description = description
    return _export_as_csv
