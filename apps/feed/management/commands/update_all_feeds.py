from django.core.management.base import BaseCommand

from apps.feed.tasks import update_all_feeds


class Command(BaseCommand):
    help = 'Update all feeds in the background'

    def handle(self, *args, **options):
        update_all_feeds.apply_async(())
        self.stdout.write(self.style.SUCCESS('UPDATING FEEDS STARTED'))
