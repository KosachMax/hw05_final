import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .constants import (
    POST_CREATOR,
    SLUG,
    USERNAME,
    POST_DETAIL_URL_NAME,
    PROFILE_URL_NAME,
    POST_COMMENT_URL_NAME,
    REVERSE_POST_CREATE,
    POST_EDIT_URL_NAME,
)
from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=POST_CREATOR)
        cls.user = User.objects.create(username=USERNAME)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug=SLUG,
            description='Test desc',
        )
        cls.second_group = Group.objects.create(
            title='New group',
            slug='new_slug',
            description='New description'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Test text'
        )
        cls.posts_count = Post.objects.count()
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Test comment'
        )
        cls.comment_count = Comment.objects.count()
        cls.REVERSE_POST_DETAIL = reverse(
            POST_DETAIL_URL_NAME,
            kwargs={'post_id': cls.post.id}
        )
        cls.REVERSE_COMMENT = reverse(
            POST_COMMENT_URL_NAME,
            kwargs={'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_is_author = Client()
        self.authorized_client_is_author.force_login(self.author)

    def test_create_post(self):
        """Форма создаст запись в БД"""
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client_is_author.post(
            REVERSE_POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            PROFILE_URL_NAME,
            args=[POST_CREATOR]),
            HTTPStatus.FOUND
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        post = Post.objects.latest('created')
        fields_in_post = (
            (post.author, self.post.author),
            (post.text, self.post.text),
            (post.group, self.group),
            (post.image, self.post.image)
        )
        for new_post, expected in fields_in_post:
            with self.subTest(new_post=expected):
                self.assertEqual(new_post, expected)

    def test_post_edit(self):
        """Форма изменит существующую запись в БД"""
        form_data_edited = {
            'text': 'Edited text',
            'group': self.second_group.id,
        }
        response = self.authorized_client.post(
            reverse(POST_EDIT_URL_NAME, args=(self.post.id,)),
            data=form_data_edited,
            follow=True
        )
        post = Post.objects.get(id=self.post.id)
        fields_in_post = (
            (post.author, self.post.author),
            (post.text, self.post.text),
            (post.group, self.group),
        )
        for new_post, expected in fields_in_post:
            with self.subTest(new_post=expected):
                self.assertEqual(new_post, expected)
        self.assertRedirects(response, self.REVERSE_POST_DETAIL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), self.posts_count)

    def test_create_comment_form(self):
        """Форма comment создаст запись в БД"""
        form_data = {
            'text': self.comment.text,
        }
        only_auth_clients = [
            self.authorized_client,
            self.authorized_client_is_author
        ]
        for client in only_auth_clients:
            response = client.post(
                self.REVERSE_COMMENT,
                data=form_data,
                follow=True
            )
            self.assertRedirects(response, self.REVERSE_POST_DETAIL)
            self.assertEqual(response.status_code, HTTPStatus.OK)
        comment = Comment.objects.get(id=self.comment.id)
        self.assertEqual(Comment.objects.count(), self.comment_count + 2)
        self.assertEqual(comment.text, self.comment.text)
