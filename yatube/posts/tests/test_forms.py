from http import HTTPStatus
import shutil
import tempfile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User
from posts.forms import PostForm
from django.core.files.uploadedfile import SimpleUploadedFile
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SLUG_1 = 'test-slug'
USER = 'user_1'
AUTHOR = 'author_1'
TEXT = 'text'
TEXT_1 = 'Тестовый текст'
TEXT_2 = 'text_2'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'

INDEX_NAME = 'posts:index'
PROFILE_NAME = 'posts:profile'
POST_DL = 'posts:post_detail'
POST_ED = 'posts:post_edit'
POST_CR = 'posts:post_create'
SIGNUP_NAME = 'users:signup'
LOGIN_NAME = 'users:login'
PROFILE_USER = reverse(PROFILE_NAME, kwargs={'username': AUTHOR})
LOGIN_1 = reverse(LOGIN_NAME)
POST_CR_1 = reverse(POST_CR)
TARGET_URL = f'{LOGIN_1}?next={POST_CR_1}'
TARGET_URL_1 = f'{LOGIN_1}?next={PROFILE_USER}'
FORM_DATA_1 = {'text': 'Тест'}
FORM_DATA_2 = {'text': TEXT_2}
FORM_DATA_3 = {'username': AUTHOR,
               'password1': '1qaz2wsxC',
               'password2': '1qaz2wsxC'}
FORM_DATA_4 = {'text': 'Просто тест'}
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
class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username=USER)
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title=TITLE,
            description=DESCRIPTION)
        cls.post = Post.objects.create(author=cls.author,
                                       text=TEXT_1,
                                       group=cls.group)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.detail = reverse(
            POST_DL, kwargs={'post_id': self.post.id})
        self.login = reverse('users:login')
        self.POST_EDIT = reverse(
            POST_ED, kwargs={'post_id': self.post.id})
        self.target_url = f'{LOGIN_1}?next={self.POST_EDIT}'

    def test_form_create_authorized_client(self):
        posts_count = Post.objects.filter(
            author=self.author).exists()
        response = self.authorized_client.post(
            reverse(POST_CR),
            data=FORM_DATA_1,
            follow=True
        )
        self.assertRedirects(response, PROFILE_USER)
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertTrue(Post.objects.filter(text=FORM_DATA_1[TEXT]).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_form_create_guests(self):
        response = self.guest.post(
            reverse(POST_CR),
            data=FORM_DATA_4,
            follow=True
        )
        post_exist = Post.objects.filter(author=self.user_1
                                         ).exists()
        self.assertEqual(post_exist, False)
        self.assertRedirects(response,
                             TARGET_URL,
                             status_code=HTTPStatus.FOUND,
                             target_status_code=HTTPStatus.OK,
                             msg_prefix='')

    def test_form_edit_post_authorized_client(self):
        posts_count = Post.objects.filter(
            author=self.author).exists()
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=FORM_DATA_2,
            follow=True
        )
        self.assertRedirects(response, self.detail)
        self.assertEqual(posts_count, Post.objects.count())
        self.assertTrue(Post.objects.filter(text=TEXT_2).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_form_edit_post_guest(self):
        posts_count = Post.objects.filter(
            author=self.user_1).exists()
        response = self.guest.post(
            self.POST_EDIT,
            data=FORM_DATA_4,
        )
        self.assertRedirects(response,
                             self.target_url,
                             status_code=HTTPStatus.FOUND,
                             target_status_code=HTTPStatus.OK,
                             msg_prefix='')
        self.assertEqual(posts_count, False)

    def test_create_post_img_authorized_client(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            POST_CR_1,
            data=FORM_DATA_IMG,
            follow=True)
        self.assertRedirects(
            response,
            PROFILE_USER)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEXT_1,
                image='posts/small.gif'
            ).exists())
