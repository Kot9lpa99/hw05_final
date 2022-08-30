from http import HTTPStatus
from django.test import Client, TestCase
from posts.models import Group, Post, User

URLS = {
    'index_1': 'posts/index.html',
    'group_1': 'posts/group_list.html',
    'profile_1': 'posts/profile.html',
    'post_detail_1': 'posts/post_detail.html',
    'post_create_and_edit': 'posts/create_post.html',
    'signup_1': 'users/signup.html',
    'login_1': 'users/login.html',
    'author_1': 'about/author.html',
    'tech_1': 'about/tech.html',
}

SLUG_1 = 'test-slug'
USER = 'user_1'
AUTHOR = 'author_1'
POST_NUM = '1'
TITLE = 'Заголовок тестовой группы'
DESCRIPTION = 'Тестовое описание группы'
TEXT1 = 'Тестовый текст, совсем тестовый'

URL_INDEX = '/'
URL_GROUP_LIST = f'/group/{SLUG_1}/'
URL_PROFILE = f'/profile/{USER}/'
URL_POST_DETAIL = f'/posts/{POST_NUM}/'
URL_CREATE_POST = '/create/'
URL_EDIT_POST = f'/posts/{POST_NUM}/edit/'
URL_SIGNUP = '/auth/signup/'
URL_LOGIN = '/auth/login/'
URL_FAKE_PAGE = '/posts/fake_page'
URL_REDIRECT = f'/auth/login/?next=/posts/{POST_NUM}/edit/'

AUTHOR_TEST = {
    URL_INDEX: HTTPStatus.OK,
    URL_GROUP_LIST: HTTPStatus.OK,
    URL_PROFILE: HTTPStatus.OK,
    URL_POST_DETAIL: HTTPStatus.OK,
    URL_CREATE_POST: HTTPStatus.OK,
    URL_EDIT_POST: HTTPStatus.OK,
    URL_SIGNUP: HTTPStatus.OK,
    URL_LOGIN: HTTPStatus.OK,
    URL_FAKE_PAGE: HTTPStatus.NOT_FOUND,
}

USER_TEST = {
    URL_INDEX: HTTPStatus.OK,
    URL_GROUP_LIST: HTTPStatus.OK,
    URL_PROFILE: HTTPStatus.OK,
    URL_POST_DETAIL: HTTPStatus.OK,
    URL_CREATE_POST: HTTPStatus.OK,
    URL_EDIT_POST: HTTPStatus.FOUND,
    URL_SIGNUP: HTTPStatus.OK,
    URL_LOGIN: HTTPStatus.OK,
    URL_FAKE_PAGE: HTTPStatus.NOT_FOUND,
}

GUEST_TEST = {
    URL_INDEX: HTTPStatus.OK,
    URL_GROUP_LIST: HTTPStatus.OK,
    URL_PROFILE: HTTPStatus.OK,
    URL_POST_DETAIL: HTTPStatus.OK,
    URL_CREATE_POST: HTTPStatus.FOUND,
    URL_EDIT_POST: HTTPStatus.FOUND,
    URL_SIGNUP: HTTPStatus.OK,
    URL_LOGIN: HTTPStatus.OK,
    URL_FAKE_PAGE: HTTPStatus.NOT_FOUND,
}

URL_ADDRESS = {
    URL_INDEX: URLS['index_1'],
    URL_GROUP_LIST: URLS['group_1'],
    URL_PROFILE: URLS['profile_1'],
    URL_POST_DETAIL: URLS['post_detail_1'],
    URL_CREATE_POST: URLS['post_create_and_edit'],
    URL_EDIT_POST: URLS['post_create_and_edit'],
    URL_LOGIN: URLS['login_1']
}


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username=USER)
        cls.author_1 = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title=TITLE,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            id='1',
            author=cls.author_1,
            text=TEXT1,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user_1)
        self.authorized_client_author.force_login(self.author_1)

    def test_url_quest(self):
        for page_url, i in GUEST_TEST.items():
            with self.subTest(page_url=page_url):
                response = self.guest_client.get(page_url)
                self.assertEqual(response.status_code, i, page_url)

    def test_redirect_guest_user_to_login(self):
        response = self.guest_client.get(URL_EDIT_POST, follow=True)
        self.assertRedirects(response, URL_REDIRECT)

    def test_url_authorized(self):
        for page_url, i in USER_TEST.items():
            with self.subTest(page_url=page_url):
                response = self.authorized_client.get(page_url)
                self.assertEqual(response.status_code, i, page_url)
        response = self.authorized_client.get(URL_CREATE_POST)
        self.assertTemplateUsed(response, URLS['post_create_and_edit'])
        response = self.guest_client.get(URL_EDIT_POST)
        self.assertEqual(response.status_code,
                         HTTPStatus.FOUND, URLS['post_create_and_edit'])

    def test_url_authorized_author(self):
        for page_url, i in AUTHOR_TEST.items():
            with self.subTest(page_url=page_url):
                response = self.authorized_client_author.get(page_url)
                self.assertEqual(response.status_code, i, page_url)
        response = self.authorized_client_author.get(URL_EDIT_POST)
        self.assertTemplateUsed(response, URLS['post_create_and_edit'])

    def test_url_address(self):
        for address, template in URL_ADDRESS.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)
