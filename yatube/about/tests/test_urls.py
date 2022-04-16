from django.contrib.auth.models import User
from django.test import TestCase, Client

from typing import NamedTuple


class TemplateUrlTuple(NamedTuple):
    template: str
    address: str


ABOUT_PAGE = TemplateUrlTuple('about/author.html', '/about/author/')
TECH_PAGE = TemplateUrlTuple('about/tech.html', '/about/tech/')

STATIC_PAGES = (ABOUT_PAGE, TECH_PAGE)


class AboutUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        #  authorized
        cls.user_logged = User.objects.create_user(username='NoName')
        cls.logged_client = Client()
        cls.logged_client.force_login(cls.user_logged)

    def test_not_authorized_urls(self):
        """Check author and tech urls for not authorized user"""
        for template, address in STATIC_PAGES:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address)
                logged_response = self.logged_client.get(address)
                self.assertTemplateUsed(guest_response, template)
                self.assertTemplateUsed(logged_response, template)
