from http import HTTPStatus

from django.test import TestCase, Client
from posts.models import Post, Group, User

from .constants import (
    SLUG,
    USERNAME,
    INDEX_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    CREATE_POST_TEMPLATE,
    UNEXISTING_URL,
    CREATE_POST_URL,
    CREATE_USER_URL,
    GROUP_LIST_URL,
    PROFILE_URL,
    CRT_USER_REDIR_FROM_EDIT_URL

)


class PostsUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_not_author = User.objects.create_user(username='not_auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug=SLUG,
            description='Test desc',
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group,
        )
        cls.POST_DETAIL_URL = f'/posts/{cls.post.id}/'
        cls.EDIT_POST_URL = f'/posts/{cls.post.id}/edit/'
        cls.COMMENT_POST_URL = f'/posts/{cls.post.id}/comment'

    def setUp(self):
        """Создаем экземпляр Юзера"""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsUrlTest.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(
            PostsUrlTest.user_not_author
        )

    def test_urls_uses_correct_template(self):
        """URL - адрес использует соответствующий шаблон"""
        templates_url_names = {
            '': INDEX_TEMPLATE,
            GROUP_LIST_URL: GROUP_LIST_TEMPLATE,
            PROFILE_URL: PROFILE_TEMPLATE,
            self.POST_DETAIL_URL: POST_DETAIL_TEMPLATE,
            CREATE_POST_URL: CREATE_POST_TEMPLATE,
            self.EDIT_POST_URL: CREATE_POST_TEMPLATE,
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_page_is_only_for_author(self):
        """Страница /post_id/edit/ доступна только автору."""
        response = self.authorized_client.get(self.EDIT_POST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_on_auth_login(self):
        pages = [
            (self.authorized_client_not_author, self.EDIT_POST_URL,
             self.POST_DETAIL_URL),
            (self.guest_client, CREATE_POST_URL,
             CREATE_USER_URL),
            (self.guest_client, self.EDIT_POST_URL,
             CRT_USER_REDIR_FROM_EDIT_URL),
        ]
        for client, path, exp_url in pages:
            with self.subTest(client=client,
                              path=path,
                              exp_url=exp_url,
                              ):
                response = client.get(path)
                self.assertRedirects(response, exp_url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_guest_client_cant_comment_posts(self):
        response = self.guest_client.get(self.COMMENT_POST_URL)
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_page_404(self):
        """Тест запроса к несуществующей странице"""
        response = self.guest_client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
