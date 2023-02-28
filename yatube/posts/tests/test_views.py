import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, User, Comment, Follow
from yatube.settings import LATEST_POSTS_COUNT

from .constants import (
    POST_CREATOR,
    SLUG,
    USERNAME,
    REVERSE_FOLLOW_INDEX,
    REVERSE_INDEX,
    REVERSE_POST_CREATE,
    REVERSE_PROFILE,
    GROUP_LIST_URL_NAME,
    SMALL_GIF
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=POST_CREATOR)
        cls.user = User.objects.create_user(username=USERNAME)
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
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
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_author_client = Client()
        cls.authorized_author_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        cache.clear()
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
        get_comment_context = response.context['comments']
        test_comments_detail = {
            get_comment_context: self.comment.text,
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
        post = response.context['post']
        test_post_detail = {post.text: self.post.text,
                            post.group: self.post.group,
                            post.author: self.post.author,
                            post.image: self.post.image,
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


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth_user')
        cls.auth_user_author = User.objects.create_user(
            username='auth_user_author'
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.auth_user_author,
        )
        cls.REVERSE_PROFILE_FOLLOW = reverse(
            'posts:profile_follow',
            kwargs={'username': cls.auth_user_author.username}
        )
        cls.REVERSE_PROFILE_UNFOLLOW = reverse(
            'posts:profile_unfollow',
            kwargs={'username': cls.auth_user_author.username}
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.auth_user)
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.auth_user_author)

    def test_auth_user_can_follow_and_unfollow_users(self):
        """Авторизованный пользователь может
        подписываться и отписываться от автора"""
        self.authorized_client.get(self.REVERSE_PROFILE_FOLLOW)
        self.assertEqual(Follow.objects.all().count(), 1)
        self.authorized_client.get(self.REVERSE_PROFILE_UNFOLLOW)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_following_author_posts_shows_on_follow_page(self):
        """Пост подписанного автора отображается на странице подписок"""
        self.authorized_client.get(self.REVERSE_PROFILE_FOLLOW)
        response = self.authorized_client.get(REVERSE_FOLLOW_INDEX)
        self.assertEqual(response.context.get('post')[0], self.post)
