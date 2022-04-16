from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Group, Post

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
