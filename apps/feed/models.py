from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Feed(TimeStampedModel):
    name = models.CharField(_('Name'), max_length=150)
    url = models.URLField(_('URL'), max_length=500, unique=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.name} - {self.url}'


class FeedItem(TimeStampedModel):
    """
    RSS Item; specs: https://www.rssboard.org/rss-2-0-1
    """
    feed = models.ForeignKey(
        Feed, verbose_name=_(
            'Feed',
        ), on_delete=models.CASCADE,
    )
    title = models.CharField(_('Title'), max_length=500)
    link = models.URLField(_('Link'), max_length=500)
    description = models.TextField(_('Description'), max_length=500)
    language = models.CharField(
        _('Language'), max_length=100, null=True, blank=True,
    )
    pub_date = models.DateTimeField(_('Published'), null=True, blank=True)
    item_id = models.CharField(
        _('Item ID'), max_length=500, null=True, blank=True,
    )
    copyright = models.CharField(
        _('Copy Right'), max_length=100, null=True, blank=True,
    )
    image = models.JSONField(_('Image'), null=True, blank=True)

    class Meta:
        ordering = ['-created', '-pub_date']

    def __str__(self):
        return f'{self.feed.name} - {self.title}'
