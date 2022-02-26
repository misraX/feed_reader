from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class AccountsViewTest(APITestCase):
    """
    Testing user registration
    """

    def setUp(self) -> None:
        self.register_url: str = reverse('accounts_register')
        self.login_url: str = reverse('accounts_login')

    def test_register_success_user(self) -> None:
        response = self.client.post(
            self.register_url, {
                'email': 'user@example.com', 'username': 'string',
                'first_name': 'string', 'last_name': 'string',
                'password': 'string',
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)['username'], 'string')

    def test_register_fail_user(self) -> None:
        # password required
        response = self.client.post(
            self.register_url, {'email': 'user@example.com'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {
                'username': ['This field is required.'],
                'password': ['This field is required.'],
            },
        )
        User.objects.create_user('test@mail.com', 'testpass')
        # user with this email already exist
        response = self.client.post(
            self.register_url, {
                'email': 'test@mail.com', 'password': 'testpass',
            },
        )

        self.assertEqual(
            json.loads(response.content), {
                'username': ['This field is required.'],
            },
        )
        self.client.post(
            self.register_url, {
                'email': 'user@example.com', 'username': 'string',
                'first_name': 'string', 'last_name': 'string', 'password': 'string',
            },
        )
        response = self.client.post(
            self.register_url, {
                'email': 'user2@example.com', 'username': 'string',
                'first_name': 'string', 'last_name': 'string',
                'password': 'string',
            },
        )
        self.assertEqual(
            json.loads(response.content), {
                'username': ['A user with that username already exists.'],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_login(self) -> None:
        User.objects.create_user('string', password='testpass')
        # user with this email already exist
        response = self.client.post(
            self.login_url, {
                'username': 'string', 'password': 'testpass',
            },
        )
        self.assertEqual(response.status_code, 200)
