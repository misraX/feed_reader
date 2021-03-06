import factory

from apps.accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """
    A factory for User
    """

    class Meta:
        model = User
        django_get_or_create = ('username',)

    password = factory.PostGenerationMethodCall('set_password', 'password')
    username = factory.Faker('first_name')
    email = factory.Faker('email')
