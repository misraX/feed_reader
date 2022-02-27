import django.test.runner
import factory
from django.conf import settings
from django.utils import translation


class Runner(django.test.runner.DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        with factory.Faker.override_default_locale(translation.to_locale(settings.LANGUAGE_CODE)):
            return super().run_tests(test_labels, extra_tests=extra_tests, **kwargs)
