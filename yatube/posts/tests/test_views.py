import shutil
import tempfile
import time
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from posts.models import Group, Post, Comment, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


SLUG_1 = 'test-slug'
USER = 'user_1'
AUTHOR = 'author_1'
POST_NUM = '1'
TITLE = 'Заголовок тестовой группы'
DESCRIPTION = 'Тестовое описание группы'
TEXT1 = 'text'
PAGE: int = 10
PAGE_TWO = '?page=2'
SEIS: int = 6

INDEX = reverse('posts:index')
GR_LIST = reverse('posts:group_list', kwargs={'slug': SLUG_1})
CR_POST = reverse('posts:post_create')
POST_DL = reverse('posts:post_detail', kwargs={'post_id': POST_NUM})
PROFILE = reverse('posts:profile', kwargs={'username': AUTHOR})
POST_EDIT = reverse('posts:post_edit', kwargs={'post_id': POST_NUM})
LOGIN = reverse('users:login')
FOLLOW = reverse('posts:follow_index')
PAGES_NAME = {
    'posts/index.html': INDEX,
    'posts/group_list.html': GR_LIST,
    'posts/create_post.html': CR_POST,
    'posts/post_detail.html': POST_DL,
    'posts/profile.html': PROFILE,
}
PRIVATE_PAGES_ONLY_USERS = {
    CR_POST: '/auth/login/?next=/create/',
    POST_EDIT: f'/auth/login/?next=/posts/{POST_NUM}/edit/'}
FORM_FIELD = {
    'text': forms.fields.CharField,
    'group': forms.models.ModelChoiceField,
    'image': forms.fields.ImageField}
SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
UPLOAD = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
FORM_DATA_IMG = {'author': 'Автор',
                 'text': 'Тестовый текст',
                 'image': UPLOAD}


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username=USER)
        cls.author_1 = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=TITLE,
            description=DESCRIPTION,
            slug=SLUG_1,
        )
        cls.post = Post.objects.create(
            id='1',
            author=cls.author_1,
            text=TEXT1,
            group=cls.group,
            image=UPLOAD,
        )
        for i in range(15, 0, -1):
            time.sleep(0.01)
            Post.objects.create(
                author=cls.author_1,
                text=f'text{i}',
                group=cls.group,
                image=UPLOAD
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author_1)

    def test_pages_uses_correct_template_authorized_client(self):
        for template, reverse_name in PAGES_NAME.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_anonymous(self):
        for reverse_name, template in PRIVATE_PAGES_ONLY_USERS.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertRedirects(response, template)

    def test_post_create_page(self):
        response = self.authorized_client_author.get(CR_POST)
        for value, expected in FORM_FIELD.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_pages(self):
        response = self.authorized_client_author.get(INDEX)
        obj = response.context['page_obj'][1]
        self.assertEqual(obj.author, self.post.author)
        self.assertEqual(obj.text, obj.text)
        self.assertTrue(obj.image, self.post.image)

    def test_group_pages(self):
        response = self.authorized_client_author.get(GR_LIST)
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.author, self.author_1)
        self.assertEqual(obj.text, obj.text)
        self.assertEqual(obj.group, self.group)
        self.assertTrue(obj.image, self.post.image)

    def test_profile_pages(self):
        response = self.authorized_client_author.get(PROFILE)
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.text, obj.text)
        self.assertEqual(obj.author, self.author_1)
        self.assertTrue(obj.image, self.post.image)

    def test_post_detail_pages(self):
        response = self.authorized_client_author.get(POST_DL)
        self.assertEqual(response.context.get('post').text, TEXT1)
        self.assertEqual(response.context.get('post').author, self.author_1)
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertTrue(response.context.get('post').image)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_post_edit(self):
        response = self.authorized_client_author.get(POST_EDIT)
        for value, expected in FORM_FIELD.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_first_and_second_pages(self):
        response = self.authorized_client_author.get(INDEX)
        self.assertEqual(len(response.context['page_obj']), PAGE)
        response = self.authorized_client_author.get(INDEX + '?page=2')
        self.assertEqual(len(response.context['page_obj']), SEIS)

    def test_group_lists_first_and_second_pages(self):
        response = self.authorized_client_author.get(GR_LIST)
        self.assertEqual(len(response.context['page_obj']), PAGE)
        response = self.authorized_client_author.get(GR_LIST + '?page=2')
        self.assertEqual(len(response.context['page_obj']), SEIS)

    def test_profile_first_and_second_pages(self):
        response = self.authorized_client_author.get(PROFILE)
        self.assertEqual(len(response.context['page_obj']), PAGE)
        response = self.authorized_client_author.get(PROFILE + '?page=2')
        self.assertEqual(len(response.context['page_obj']), SEIS)

    def test_create_comment_authorized_client(self):
        comments_count = Comment.objects.count()
        new_comment = (Comment.objects.create(
            post=self.post,
            author=self.user_1, text=TEXT1)).text
        response = self.authorized_client_author.get(POST_DL)
        comment_2 = response.context['comments'][0].text
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment_2, new_comment)

    def test_cache_index(self):
        response = self.authorized_client_author.get(INDEX)
        posts = response.content
        Post.objects.create(
            text=TEXT1,
            author=self.author_1,
        )
        response_1 = self.authorized_client_author.get(INDEX)
        posts_1 = response_1.content
        self.assertEqual(posts_1, posts)
        cache.clear()
        response_2 = self.authorized_client_author.get(INDEX)
        posts_2 = response_2.content
        self.assertNotEqual(posts_1, posts_2)

    def test_user_unsub_and_sub(self):
        user2 = User.objects.create_user(username='User2')
        Follow.objects.create(user=self.author_1, author=user2)
        followers_count = Follow.objects.filter(
            user=self.author_1, author=user2).count()
        self.assertEqual(followers_count, 1)
        self.guest_client.get(PROFILE)
        followers_count = Follow.objects.filter(
            user=self.user_1, author=user2).count()
        self.assertEqual(followers_count, 0)

    def test_follow_post_exists_in_follow_index(self):
        user2 = User.objects.create_user(username='User2')
        post = Post.objects.create(text='Проверка подписки', author=user2)
        Follow.objects.create(user=self.author_1, author=user2)
        response = self.authorized_client_author.get(FOLLOW)
        post_text1 = response.context['page_obj'][0].text
        self.assertEqual(post.text, post_text1)

    def test_unfollow_post_does_not_exists_in_follow_index(self):
        user2 = User.objects.create_user(username='User2')
        post = Post.objects.create(text='Проверка подписки', author=user2)
        test_client = Client()
        test_client.force_login(user2)
        Follow.objects.create(user=user2, author=self.author_1)
        response = test_client.get(FOLLOW)
        post_text1 = response.context['page_obj'][0].text
        self.assertNotEqual(post.text, post_text1)
