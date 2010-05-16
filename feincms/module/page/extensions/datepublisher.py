"""
Allows setting a date range for when the page is active. Modifies the active()
manager method so that only pages inside the given range are used in the default
views and the template tags.

Depends on the page class having a "active_filters" list that will be used by
the page's manager to determine which entries are to be considered active.
"""
# ------------------------------------------------------------------------

from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

# ------------------------------------------------------------------------
def format_date(d, if_none=''):
    """
    Format a date in a nice human readable way: Omit the year if it's the current
    year. Also return a default value if no date is passed in.
    """

    if d is None: return if_none

    now = datetime.now()
    fmt = (d.year == now.year) and '%d.%m' or '%d.%m.%Y'
    return d.strftime(fmt)

# ------------------------------------------------------------------------
def register(cls, admin_cls):
    cls.add_to_class('publication_date', models.DateTimeField(_('publication date'),
        default=datetime.now))
    cls.add_to_class('publication_end_date', models.DateTimeField(_('publication end date'),
        blank=True, null=True,
        help_text=_('Leave empty if the entry should stay active forever.')))

    if hasattr(cls.objects, 'add_to_active_filters'):
        cls.objects.add_to_active_filters(
            Q(publication_date__lte=datetime.now) &
            (Q(publication_end_date__isnull=True) | Q(publication_end_date__gt=datetime.now))
            )

    def datepublisher_admin(self, page):
        return u'%s &ndash; %s' % (
            format_date(page.publication_date),
            format_date(page.publication_end_date, '&infin;'),
            )
    datepublisher_admin.allow_tags = True
    datepublisher_admin.short_description = _('visible from - to')

    admin_cls.datepublisher_admin = datepublisher_admin
    try:
        pos = admin_cls.list_display.index('is_visible_admin')
    except ValueError:
        pos = len(admin_cls.list_display)

    admin_cls.list_display.insert(pos + 1, 'datepublisher_admin')

# ------------------------------------------------------------------------
