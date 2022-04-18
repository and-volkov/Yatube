import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings

from ..models import Comment, Group, Post

GROUP_SLUG = 'test-group'

POST_CREATE_PAGE = reverse('posts:post_create')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTest(TestCase):
    USER_NAME = 'First'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.USER_NAME)
        cls.group = Group.objects.create(
            title='Test group',
            slug=GROUP_SLUG,
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group
        )
        cls.POST_COUNT = Post.objects.count()
        cls.POST_ID = cls.post.id
        cls.PROFILE_PAGE = reverse('posts:profile', kwargs=({
            'username': cls.user.username}))
        cls.POST_EDIT_PAGE = reverse('posts:post_edit',
                                     kwargs={'post_id': cls.POST_ID})
        cls.POST_DETAIL_PAGE = reverse('posts:post_detail',
                                       kwargs={'post_id': cls.POST_ID})

    def setUp(self):
        self.form_data = {
            'text': 'Test form text',
        }
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form_works_correctly(self):
        """Check post created successfully"""
        response = self.authorized_client.post(
            POST_CREATE_PAGE,
            data=self.form_data,
            follow=True
        )
        # Check redirect
        self.assertRedirects(response, self.PROFILE_PAGE)
        # Check post created successfully
        self.assertEqual(Post.objects.count(), self.POST_COUNT + 1)

    def test_post_edit_form_works_correctly(self):
        """Check post edited successfully"""
        response = self.authorized_client.post(
            self.POST_EDIT_PAGE,
            data=self.form_data,
            follow=True
        )
        # Check redirect
        self.assertRedirects(response,
                             self.POST_DETAIL_PAGE)
        # Check edited first post
        self.assertEqual(Post.objects.get(pk=self.POST_ID).text,
                         self.form_data['text'])


class CommentFormCreationTest(TestCase):
    USER_NAME = 'Second'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.USER_NAME)
        cls.group = Group.objects.create(
            title='Test group',
            slug=GROUP_SLUG,
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
        )
        cls.POST_ID = cls.post.id
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Test comment',
            post_id=cls.POST_ID
        )
        cls.COMMENT_COUNT = Comment.objects.count()
        cls.POST_PAGE = reverse('posts:post_detail',
                                kwargs={'post_id': cls.POST_ID})
        cls.ADD_COMMENT_PAGE = reverse('posts:add_comment',
                                       kwargs={'post_id': cls.POST_ID})

    def setUp(self):
        self.comment_data = {
            'text': 'Test comment text'
        }
        # authorized user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # not authorized user
        self.guest_client = Client()

    def test_comment_created_successfully(self):
        """Check comment created successfully"""
        response = self.authorized_client.post(
            self.ADD_COMMENT_PAGE,
            data=self.comment_data,
            follow=True
        )
        # Check redirect
        self.assertRedirects(response, self.POST_PAGE)
        # Check comment created successfully
        self.assertEqual(Comment.objects.count(), self.COMMENT_COUNT + 1)

    def test_comment_form_available_only_for_authorized_users(self):
        """Unauthorized user can't comment posts"""
        # send form as guest. should redirect to login page
        guest_response = self.guest_client.post(
            self.ADD_COMMENT_PAGE,
            data=self.comment_data,
            follow=True
        )
        self.assertRedirects(
            guest_response,
            f'/auth/login/?next=/posts/{self.POST_ID}/comment/')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostWithImageFormTest(TestCase):
    USER_NAME = 'Third'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Добавлен сюда, т.к. если находится только в teardown папка остается
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        cls.user = User.objects.create_user(username=cls.USER_NAME)
        cls.group = Group.objects.create(
            title='Test group',
            slug=GROUP_SLUG,
            description='Test description'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group
        )
        cls.PROFILE_PAGE = reverse('posts:profile', kwargs=({
            'username': cls.user.username}))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_count = Post.objects.count()

    def test_create_post_form_with_image(self):
        """Should create new post with image"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test text',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            POST_CREATE_PAGE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.PROFILE_PAGE)
        self.assertEqual(Post.objects.count(), self.post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test text',
                image='posts/small.gif'
            ).exists()
        )

    # Added test for not image file
    def test_bad_file_not_uploading(self):
        """shouldn't create new post with broken file"""
        not_gif = (
            b'Random stuff'
        )
        uploaded = SimpleUploadedFile(
            name='not_gif.gif',
            content=not_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test text',
            'image': uploaded,
        }
        self.authorized_client.post(
            POST_CREATE_PAGE,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertFalse(
            Post.objects.filter(
                text='Test text',
                image='posts/not_gif.gif'
            )
        )
