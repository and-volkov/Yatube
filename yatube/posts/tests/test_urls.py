from django.contrib.auth.models import User
from django.test import TestCase, Client

from typing import NamedTuple

from ..models import Group, Post


class TemplateUrlTuple(NamedTuple):
    template: str
    address: str


GROUP_SLUG = 'test-slug'

INDEX_PAGE = TemplateUrlTuple('posts/index.html', '/')
GROUP_PAGE = TemplateUrlTuple(
    'posts/group_list.html',
    f'/group/{GROUP_SLUG}/'
)
POST_CREATE_PAGE = TemplateUrlTuple(
    'posts/create_post.html',
    '/create/'
)


class PostUrlTest(TestCase):
    AUTHOR_NAME = 'author'
    RANDOM_NAME = 'random'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_random = User.objects.create_user(username=cls.RANDOM_NAME)
        cls.user_author = User.objects.create_user(username=cls.AUTHOR_NAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=GROUP_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост ',
        )
        cls.POST_ID = cls.post.id

        cls.AUTHOR_PROFILE_PAGE = TemplateUrlTuple(
                                'posts/profile.html',
                                f'/profile/'
                                f'{cls.AUTHOR_NAME}/'
                            )
        cls.POST_PAGE = TemplateUrlTuple(
                        'posts/post_detail.html',
                        f'/posts/{cls.POST_ID}/'
                    )
        cls.POST_EDIT_PAGE = TemplateUrlTuple(
                        'posts/create_post.html',
                        f'/posts/{cls.POST_ID}/edit/'
                    )

    def setUp(self):
        #  not authorized
        self.guest_client = Client()
        #  authorized, w/o posts
        self.random_user_client = Client()
        self.random_user_client.force_login(self.user_random)
        #  authorized post author
        self.author_user_client = Client()
        self.author_user_client.force_login(self.user_author)

    #  Check common urls for all types of users
    def test_common_urls_uses_correct_template(self):
        """Check common urls templates usage"""
        common_template_url_names = (
                                    INDEX_PAGE,
                                    GROUP_PAGE,
                                    self.AUTHOR_PROFILE_PAGE,
                                    self.POST_PAGE
                                )
        for template, address in common_template_url_names:
            with self.subTest(address=address):
                #  response for all types of users
                guest_response = self.guest_client.get(address)
                random_user_response = self.random_user_client.get(address)
                author_response = self.author_user_client.get(address)

                self.assertTemplateUsed(guest_response, template)
                self.assertTemplateUsed(random_user_response, template)
                self.assertTemplateUsed(author_response, template)

    def test_post_create_url_uses_template_or_redirect(self):
        """Check post create url.
        Should use template for authorized user or redirect for guest user"""
        guest_response = self.guest_client.get(
                                            POST_CREATE_PAGE.address,
                                            follow=True
                                        )
        random_user_response = self.random_user_client.get(
                                                    POST_CREATE_PAGE.address)
        author_response = self.author_user_client.get(POST_CREATE_PAGE.address)

        self.assertRedirects(guest_response, '/auth/login/?next=/create/')
        self.assertTemplateUsed(
            random_user_response,
            POST_CREATE_PAGE.template
        )
        self.assertTemplateUsed(author_response, POST_CREATE_PAGE.template)

    def test_post_edit_url_uses_template_or_redirect(self):
        """Check post edit url.
        Should use template for author or redirect for random, guest user"""
        guest_response = self.guest_client.get(
                                        self.POST_EDIT_PAGE.address,
                                        follow=True
                                    )
        random_user_response = self.random_user_client.get(
                                                self.POST_EDIT_PAGE.address,
                                                follow=True
                                            )
        author_response = self.author_user_client.get(
                                                self.POST_EDIT_PAGE.address)

        self.assertRedirects(guest_response, f'/posts/{self.POST_ID}/')
        self.assertRedirects(random_user_response, f'/posts/{self.POST_ID}/')
        self.assertTemplateUsed(author_response, self.POST_EDIT_PAGE.template)

    def test_non_existing_page_return_404(self):
        """Not existing page should return 404 error, and show custom view"""
        address = 'not_exist'
        error = 404
        template = 'core/404.html'

        guest_response = self.guest_client.get(address)
        random_user_response = self.random_user_client.get(address)
        author_response = self.author_user_client.get(address)

        # check error response
        self.assertEqual(guest_response.status_code, error)
        self.assertEqual(random_user_response.status_code, error)
        self.assertEqual(author_response.status_code, error)

        # check custom view
        self.assertTemplateUsed(guest_response, template)
        self.assertTemplateUsed(random_user_response, template)
        self.assertTemplateUsed(author_response, template)
