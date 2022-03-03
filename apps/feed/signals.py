import logging

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from apps.feed.models import FAILED
from apps.feed.models import FeedUpdateHistory

logger = logging.getLogger('feed_parser')


@receiver(post_save, sender=FeedUpdateHistory)
def handle_status_update(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    Trigger failure to notify the user.

    :param sender:
    :param instance:
    :param created:
    :param raw:
    :param using:
    :param update_fields:
    :param kwargs:
    :return:
    """
    msgs = f'Feed {instance.feed.url} failed to update, you can still force updating the feed using ' \
           f" {reverse('force-update-detail', kwargs={'pk': instance.feed.id})}"
    if instance.status == FAILED:
        send_mail(
            f'Feed {instance.feed.url} failed to update',
            msgs,
            'from@example.com',
            [f'{instance.feed.user.email}'],
        )
        logger.info(instance)
