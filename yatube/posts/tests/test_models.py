from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client, TestCase

from ..models import Comment, Follow, Group, Post

GROUP_SLUG = 'test-slug'


class PostModelTest(TestCase):
    USER_NAME = 'NoName'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.USER_NAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=GROUP_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост ' * 3,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        expected_post_str = post.text[:15]
        expected_group_str = group.title
        self.assertEqual(expected_post_str, str(post))
        self.assertEqual(expected_group_str, str(group))


class FollowModelTest(TestCase):
    USER_NAME = 'User'
    AUTHOR_NAME = 'Author'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.USER_NAME)
        cls.author = User.objects.create_user(username=cls.AUTHOR_NAME)

    def test_user_cant_follow_himself(self):
        """User can't follow himself. Follow objects count should be 0"""
        self.user_client = Client()
        self.user_client.force_login(self.user)
        follow_page = reverse(
            'posts:profile_follow',
            kwargs={'username': self.USER_NAME}
        )
        response = self.user_client.get(follow_page)
        self.assertEqual(Follow.objects.count(), 0)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.USER_NAME})
        )

    def test_follow_object_unique(self):
        """Check follow objects have different pk"""
        first_object = Follow.objects.create(
            user=self.user,
            author=self.author
        )
        second_object = Follow.objects.create(
            user=self.author,
            author=self.user
        )
        self.assertNotEqual(first_object.pk, second_object.pk)


class CommentModelTest(TestCase):
    USER_NAME = 'NoName'
    COMMENT_AUTHOR = 'Commentator'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.USER_NAME)
        cls.commentator = User.objects.create_user(username=cls.COMMENT_AUTHOR)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=GROUP_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост ' * 3,
        )

    def setUp(self):
        self.commentator_client = Client()
        self.commentator_client.force_login(self.commentator)
        Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Comment test text' * 3,
        )

    def test_comment_created_successfully(self):
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, Comment.objects.count())

    def test_str_func(self):
        comment = Comment.objects.get(pk=1)
        expected_comment_text = comment.text[:15]
        self.assertEqual(expected_comment_text, str(comment))
