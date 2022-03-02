from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import StatusModel
from model_utils.models import TimeStampedModel

ETAG = 'etag'
MODIFIED = 'modified'
INITIATED = 'initiated'
UPDATING = 'updating'
FAILED = 'failed'
DONE = 'done'
MODIFIED_METHODS_CHOICES = (
    ('ETAG', ETAG),
    ('MODIFIED', MODIFIED),
)

FEED_UPDATE_CHOICES = (
    ('INITIATE', INITIATED),
    ('UPDATING', UPDATING),
    ('FAILED', FAILED),
    ('DONE', DONE),
)


class FeedUpdateHistory(StatusModel, TimeStampedModel):
    """
    Holds data related to the update history
    Feed updates can be done periodically or through a user
    The periodic tasks is a system update, that means the user will be null.
    """
    STATUS = FEED_UPDATE_CHOICES
    bozo = models.BooleanField(default=False, null=True, blank=True)
    feed = models.ForeignKey(
        'Feed', verbose_name=_(
            'Feed',
        ), on_delete=models.CASCADE,
    )
    errors = models.JSONField(verbose_name=_('Errors'), null=True, blank=True)
    updated_by = models.ForeignKey(
        User, verbose_name=_(
            'Update By',
        ), on_delete=models.CASCADE, null=True, blank=False,
    )

    class Meta:
        ordering = ['-created']
        get_latest_by = ['-created']

    def __str__(self):
        return f'{self.feed.name} | {self.feed.url} | {self.status}'


class Feed(TimeStampedModel):
    """
    Global Feeds, holds site wide feeds, they can be registered by a user or globally without a user
    """
    name = models.CharField(_('Name'), max_length=150)
    url = models.URLField(
        _('URL'), max_length=500,
        db_index=True, unique=True,
    )
    user = models.ForeignKey(
        User, verbose_name=_(
            'User',
        ), null=True, blank=True, on_delete=models.CASCADE,
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

    class Meta:
        ordering = ['-created']
        get_latest_by = ['-created']

    def __str__(self):
        return f'{self.user.username} | {self.name} - {self.url}'

    def feed_update_history_latest(self):
        try:
            last_updated_history = FeedUpdateHistory.objects.filter(
                feed=self,
            ).latest()
            return last_updated_history
        except FeedUpdateHistory.DoesNotExist:
            return {}


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
    the reader board can include many feeds' item
    """
    user = models.ForeignKey(
        User, verbose_name=_(
            'User',
        ), on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        FeedItem, verbose_name=_(
            'Feed Item',
        ), on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-created']
        unique_together = ['user', 'item']

    def __str__(self):
        return f'{self.user.username} | {self.item}'
