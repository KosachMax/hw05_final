import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, User, Comment
from yatube.settings import LATEST_POSTS_COUNT

from .constants import (
    POST_CREATOR,
    SLUG,
    USERNAME,
    REVERSE_INDEX,
    REVERSE_POST_CREATE,
    REVERSE_PROFILE,
    GROUP_LIST_URL_NAME,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=POST_CREATOR)
        cls.user = User.objects.create_user(username=USERNAME)
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
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Test text',
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Test comment'
        )
        cls.REVERSE_POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )
        cls.REVERSE_POST_EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id}
        )
        cls.REVERSE_GROUP_LIST = reverse(
            GROUP_LIST_URL_NAME,
            kwargs={"slug": cls.group.slug}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиенты для тестов"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(REVERSE_INDEX)
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.author,
        )
        response_old = self.authorized_client.get(REVERSE_INDEX)
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(REVERSE_INDEX)
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_index_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.guest_client.get(REVERSE_INDEX)
        expected = list(Post.objects.all()[:LATEST_POSTS_COUNT])
        self.assertEqual(list(response.context["page_obj"]), expected)
        self.assertContains(response, '<img')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.guest_client.get(self.REVERSE_GROUP_LIST)
        expected = list(
            self.group.posts.all()[:LATEST_POSTS_COUNT]
        )
        self.assertEqual(list(response.context["page_obj"]), expected)
        self.assertContains(response, '<img')

    def test_comment_show_correct_context(self):
        response = self.authorized_client.get(self.REVERSE_POST_DETAIL)
        get_context = response.context['comments']
        test_comments_detail = {
            get_context: self.comment.text,
        }
        for value, expected in test_comments_detail.items():
            self.assertEqual(test_comments_detail[value], expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.guest_client.get(REVERSE_PROFILE)
        expected = list(
            self.user.posts.all()[:LATEST_POSTS_COUNT]
        )
        self.assertEqual(list(response.context["page_obj"]), expected)
        self.assertContains(response, '<img')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.REVERSE_POST_DETAIL)
        get_context = response.context['post']
        test_post_detail = {get_context.text: self.post.text,
                            get_context.group: self.post.group,
                            get_context.author: self.post.author,
                            get_context.image: self.post.image,
                            }
        for value, expected in test_post_detail.items():
            self.assertEqual(test_post_detail[value], expected)
            self.assertContains(response, '<img')

    def test_create_post_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(REVERSE_POST_CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.REVERSE_POST_EDIT
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
