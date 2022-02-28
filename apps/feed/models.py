from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

ETAG = 'etag'
MODIFIED = 'modified'
MODIFIED_METHODS_CHOICES = (
    ('ETAG', ETAG),
    ('MODIFIED', MODIFIED),
)


class Feed(TimeStampedModel):
    """
    Global Feeds, holds site wide feeds, they can be registered by a user or globally without a user
    """
    name = models.CharField(_('Name'), max_length=150)
    url = models.URLField(
        _('URL'), max_length=500,
        db_index=True, unique=True,
    )
    modified_method = models.CharField(
        _('Modified method'), choices=MODIFIED_METHODS_CHOICES, null=True, blank=True,
        max_length=100,
    )
    source_etag = models.CharField(
        _('Etag'), null=True, blank=True, max_length=500,
    )
    source_modified_at = models.CharField(
        _('Source modified at'), null=True, blank=True, max_length=500,
    )
    user = models.ForeignKey(
        User, verbose_name=_(
            'User',
        ), null=True, blank=True, on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.name} - {self.url}'


class FeedItemManage(models.Manager):
    pass


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
    pub_date = models.DateTimeField(
        _('Published'), null=True, blank=True, db_index=True,
    )
    item_id = models.CharField(
        _('Item ID'), max_length=500, null=True, blank=True,
    )
    copyright = models.CharField(
        _('Copy Right'), max_length=100, null=True, blank=True,
    )
    image = models.JSONField(_('Image'), null=True, blank=True)
    objects = FeedItemManage()

    class Meta:
        ordering = ['-created', '-pub_date']

    def __str__(self):
        return f'{self.feed.name} - {self.title}'


class Subscribe(TimeStampedModel):
    """
    Subscription holds the user's feed subscription,
    The main idea here is simple, one user can have many feeds
    but only one subscription, this is a simple subscription mechanism.
    """
    user = models.OneToOneField(
        User, verbose_name=_(
            'User',
        ), on_delete=models.CASCADE,
    )
    feeds = models.ManyToManyField(
        Feed, verbose_name=_(
            'Feed',
        ),
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.user.username}'


class Reader(TimeStampedModel):
    """
    Same as the subscription model, the user can have one reader board,
    the reader board can include many feeds' items
    """
    user = models.OneToOneField(
        User, verbose_name=_(
            'User',
        ), on_delete=models.CASCADE,
    )
    items = models.ManyToManyField(
        FeedItem, verbose_name=_(
            'Feed Item',
        ),
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.user.username}'
