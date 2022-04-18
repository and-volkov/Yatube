from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from django import forms

from typing import NamedTuple
import shutil
import tempfile

from ..models import Follow, Group, Post
from ..forms import PostForm


# For temp images
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TemplateReverseName(NamedTuple):
    template: str
    reverse_name: str


USER_NAME = 'NoName'
POSTS_PER_PAGE = settings.POSTS_PER_PAGE

FIRST_GROUP_SLUG = 'test-slug-1'
SECOND_GROUP_SLUG = 'test-slug-2'
INDEX_PAGE = TemplateReverseName('posts/index.html', reverse('posts:index'))
POST_CREATE_PAGE = TemplateReverseName(
                'posts/create_post.html',
                reverse('posts:post_create')
                )
FIRST_GROUP_PAGE = TemplateReverseName(
                'posts/group_list.html',
                reverse(
                    'posts:group_list',
                    kwargs={'slug': FIRST_GROUP_SLUG}
                    )
                )
SECOND_GROUP_PAGE = TemplateReverseName(
                'posts/group_list.html',
                reverse(
                    'posts:group_list',
                    kwargs={'slug': SECOND_GROUP_SLUG}
                    )
                )
PROFILE_PAGE = TemplateReverseName(
            'posts/profile.html',
            reverse(
                'posts:profile',
                kwargs={'username': USER_NAME}
                )
            )


class PostViewsTest(TestCase):
    POSTS_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.group = Group.objects.create(
            title='Test group',
            slug=FIRST_GROUP_SLUG,
            description='Test description'
        )
        # Create 13 posts for paginator tests
        for i in range(cls.POSTS_COUNT):
            Post.objects.create(
                author=cls.user,
                text='Test text',
                group=cls.group
            )
        cls.FIRST_POST_ID = Post.objects.first().id
        cls.POST_DETAIL_PAGE = TemplateReverseName(
                        'posts/post_detail.html',
                        reverse(
                            'posts:post_detail',
                            kwargs={'post_id': cls.FIRST_POST_ID}
                            )
                        )
        cls.POST_EDIT_PAGE = TemplateReverseName(
                        'posts/create_post.html',
                        reverse(
                            'posts:post_edit',
                            kwargs={'post_id': cls.FIRST_POST_ID}
                            )
                        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Tuple with all pages
        self.ALL_PAGES = (
            INDEX_PAGE,
            FIRST_GROUP_PAGE,
            PROFILE_PAGE,
            self.POST_DETAIL_PAGE,
            POST_CREATE_PAGE,
            self.POST_EDIT_PAGE
        )

    #  Check used templates
    def test_pages_use_correct_template(self):
        """Check views use correct html templates"""
        for template, reverse_name in self.ALL_PAGES:
            # if one template used for different pages (tuple of pages)
            if type(reverse_name) is tuple:
                for name in reverse_name:
                    response = self.authorized_client.get(name)
                    self.assertTemplateUsed(response, template)
            else:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    # Test context for index page
    def test_index_page_show_correct_context(self):
        """index post formed with correct context"""
        response = self.authorized_client.get(INDEX_PAGE.reverse_name)

        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_author = first_object.author.username

        self.assertEqual(post_text, 'Test text')
        self.assertEqual(post_author, self.user.username)

    # Test context for group_list page
    def test_group_list_page_show_correct_context(self):
        """Group page formed with correct context"""
        response = self.authorized_client.get(FIRST_GROUP_PAGE.reverse_name)

        first_object = response.context['page_obj'][0]
        group_title = first_object.group.title
        group_description = first_object.group.description
        group_slug = first_object.group.slug

        self.assertEqual(group_title, 'Test group')
        self.assertEqual(group_description, 'Test description')
        self.assertEqual(group_slug, FIRST_GROUP_SLUG)

    # Test context for profile page
    def test_profile_page_show_correct_context(self):
        """Profile page formed with correct context"""
        response = self.authorized_client.get(PROFILE_PAGE.reverse_name)

        first_object = response.context['page_obj'][0]
        profile_author = first_object.author.username

        self.assertEqual(profile_author, self.user.username)

    # Test context for post_detail page
    def test_post_detail_page_show_correct_context(self):
        """Post_detail page formed with correct context"""
        response = self.authorized_client.get(
                                        self.POST_DETAIL_PAGE.reverse_name)

        detail_post = response.context.get('post')
        post_detail_post_count = response.context.get('post_count')
        post_detail_title = response.context.get('title')

        self.assertEqual(detail_post, Post.objects.get(pk=self.FIRST_POST_ID))
        self.assertEqual(post_detail_post_count, self.POSTS_COUNT)
        self.assertEqual(
            post_detail_title,
            f'Пост {Post.objects.get(pk=self.FIRST_POST_ID).text[:30]}'
        )

    # Test post_create form and post_edit form (same fields)
    def test_post_create_edit_forms_page(self):
        """Create and edit post formed correctly"""
        # form fields for create and edit post
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField
        }
        # list of responses for post_create and post_edit
        responses = [
            self.authorized_client.get(POST_CREATE_PAGE.reverse_name),
            self.authorized_client.get(self.POST_EDIT_PAGE.reverse_name)
        ]
        # Check form is PostForm
        for response in responses:
            response_form = response.context.get('form')
            self.assertIsInstance(response_form, PostForm)
        # Check is_edit context for post_edit
        form_is_edit = responses[1].context.get('is_edit')
        self.assertEqual(form_is_edit, True)
        # Check form fields
        for response in responses:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    # Test for paginator
    def test_pages_paginator(self):
        """Pages paginator shows 10 posts per page"""
        # Pages with paginator
        pages = [
            INDEX_PAGE.template,
            FIRST_GROUP_PAGE.template,
            PROFILE_PAGE.template
        ]
        # Test first page
        for template, page in self.ALL_PAGES:
            if template in pages:
                with self.subTest(page=page):
                    # First page contains 10 posts
                    response = self.authorized_client.get(page)
                    self.assertEqual(
                        len(response.context['page_obj']),
                        POSTS_PER_PAGE
                    )
                    # Second page contains 3 posts
                    response = self.authorized_client.get(page + '?page=2')
                    self.assertEqual(
                        len(response.context['page_obj']),
                        self.POSTS_COUNT - POSTS_PER_PAGE
                    )


class PostCreationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        # First group (post group)
        cls.first_group = Group.objects.create(
            title='Test group 1',
            slug=FIRST_GROUP_SLUG,
            description='Test description 1'
        )
        # Second group (empty)
        cls.second_group = Group.objects.create(
            title='Test group 2',
            slug=SECOND_GROUP_SLUG,
            description='Test description 2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.first_group
        )
        cls.POST_ID = cls.post.id

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Check post with group created at correct pages
    def test_post_created_at_correct_pages(self):
        """New post created at correct pages"""
        pages = [
            INDEX_PAGE.reverse_name,
            FIRST_GROUP_PAGE.reverse_name,
            PROFILE_PAGE.reverse_name
        ]
        for page in pages:
            response = self.authorized_client.get(page)
            post = response.context['page_obj'][0]

            self.assertEqual(post.pk, self.POST_ID)

    # Check post not in empty group
    def test_post_created_at_correct_group_page(self):
        """New post at correct group page"""
        post_page_response = self.authorized_client.get(
                                                FIRST_GROUP_PAGE.reverse_name)
        second_group_page_response = self.authorized_client.get(
                                                SECOND_GROUP_PAGE.reverse_name)
        post_page = post_page_response.context['page_obj']
        second_group_page = second_group_page_response.context['page_obj']

        self.assertNotEqual(post_page, second_group_page)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostWithImageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.group = Group.objects.create(
            title='Test group',
            slug=FIRST_GROUP_SLUG,
            description='Test description'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
            image=uploaded
        )
        cls.FIRST_POST_ID = Post.objects.first().id
        cls.POST_DETAIL_PAGE = TemplateReverseName(
                                    'posts/post_detail.html',
                                    reverse(
                                        'posts:post_detail',
                                        kwargs={'post_id': cls.FIRST_POST_ID}
                                        )
                                    )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Tuple with index, group and profile pages
        self.TEST_PAGES = (INDEX_PAGE,
                           FIRST_GROUP_PAGE,
                           PROFILE_PAGE)

    def test_index_with_image_page_show_correct_context(self):
        """pages with images using correct context"""
        for page in self.TEST_PAGES:
            response = self.authorized_client.get(page.reverse_name)
            post = response.context['page_obj'][0]
            post_image = post.image
            self.assertEqual(post_image, 'posts/small.gif')

    def test_post_detail_with_image_page_show_correct_context(self):
        """post detail with image using correct context"""
        response = self.authorized_client.get(
            self.POST_DETAIL_PAGE.reverse_name)
        detail_post = response.context.get('post')
        detail_post_image = detail_post.image
        self.assertEqual(detail_post_image, 'posts/small.gif')


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text'
        )
        cls.POST_ID = cls.post.id

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_cache(self):
        """Deleted post should be kept in cache until cache is cleared"""
        post = Post.objects.get(pk=self.POST_ID)
        response_before_delete = self.guest_client.get(
                                                INDEX_PAGE.reverse_name)
        post.delete()
        # save content after post delete for test
        response_after_delete = self.guest_client.get(
                                                INDEX_PAGE.reverse_name)
        self.assertEqual(
            response_before_delete.content,
            response_after_delete.content
        )
        cache.clear()
        response_cache_cleared = self.guest_client.get(
                                                INDEX_PAGE.reverse_name)
        self.assertNotEqual(
            response_after_delete.content,
            response_cache_cleared.content
        )


class FollowTest(TestCase):
    FOLLOWER_NAME = 'Follower'
    NOT_FOLLOWER_NAME = 'NotFollower'
    AUTHOR_NAME = 'Author'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=cls.AUTHOR_NAME)
        cls.follower = User.objects.create_user(username=cls.FOLLOWER_NAME)
        cls.not_follower = User.objects.create_user(
            username=cls.NOT_FOLLOWER_NAME)

        cls.group = Group.objects.create(
            title='Test group',
            slug=FIRST_GROUP_SLUG,
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Test text',
            group=cls.group
        )
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.author
        )

        cls.FOLLOW_INDEX_PAGE = reverse('posts:follow_index')
        cls.FOLLOW_PAGE = reverse(
            'posts:profile_follow',
            kwargs={'username': cls.AUTHOR_NAME}
        )
        cls.UNFOLLOW_PAGE = reverse(
            'posts:profile_unfollow',
            kwargs={'username': cls.AUTHOR_NAME}
        )
        cls.AUTHOR_PAGE = reverse(
            'posts:profile',
            kwargs={'username': cls.AUTHOR_NAME}
        )

    def setUp(self):
        # log follower
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        # log not follower
        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.not_follower)

    def test_unfollow_views(self):
        """user can unfollow other users"""
        unfollow_response = self.follower_client.get(self.UNFOLLOW_PAGE)
        # redirect after unfollow
        self.assertRedirects(unfollow_response, self.AUTHOR_PAGE)
        # unfollow
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_views(self):
        """user can follow other users"""
        follow_response = self.not_follower_client.get(self.FOLLOW_PAGE)
        # redirect after follow
        self.assertRedirects(follow_response, self.AUTHOR_PAGE)
        # follow
        self.assertEqual(Follow.objects.count(), 2)

    def test_guest_follow_redirect(self):
        """guest user should be redirected to login page"""
        self.guest_client = Client()
        guest_response = self.guest_client.get(self.FOLLOW_PAGE)
        self.assertRedirects(
            guest_response,
            f'/auth/login/?next=/profile/'
            f'{self.AUTHOR_NAME}/follow/'
        )

    def test_follow_index_page(self):
        """follow index page should have 1 post for follower
         and 0 for not follower"""
        # check follower
        follower_response = self.follower_client.get(self.FOLLOW_INDEX_PAGE)
        follower_index = follower_response.context['page_obj']
        self.assertTrue(follower_index)
        # check not follower
        not_follower_response = self.not_follower_client.get(
                                                        self.FOLLOW_INDEX_PAGE)
        not_follower_index = not_follower_response.context['page_obj']
        self.assertFalse(not_follower_index)
