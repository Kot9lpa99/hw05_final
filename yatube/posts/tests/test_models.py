from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()

SLUG = 'test-slug'
AUTHOR = 'auth'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'
TEXT1 = 'Тестовый текст2'
PYATNADCAT: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT1,
        )

    def test_models_have_correct_object_names(self):
        test_group = self.group
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(test_group))

    def test_model_post(self):
        test_post = self.post
        expected_object_name = self.post.text[:PYATNADCAT]
        self.assertEqual(expected_object_name, str(test_post))
