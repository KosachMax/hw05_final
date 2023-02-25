from http import HTTPStatus

from django.test import TestCase, Client

AUTHOR_URL = '/about/author/'
TECH_URL = '/about/tech/'


class StaticPagesURLTests(TestCase):
    def setUp(self):
        """Создаем неавторизованный клиент"""
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/author/."""
        templates = [AUTHOR_URL, TECH_URL]
        for address in templates:
            with self.subTest(address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/."""
        templates_url_names = {AUTHOR_URL: 'about/author.html',
                               TECH_URL: 'about/tech.html'}
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
