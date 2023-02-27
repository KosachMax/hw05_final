from django.test import TestCase
from django.urls import reverse

from .constants import (
    POST_ID,
    SLUG,
    USERNAME,
    CREATE_POST_URL,
    GROUP_LIST_URL,
    PROFILE_URL,
    POST_COMMENT,
    FOLLOW_PAGE,
    PROFILE_FOLLOW,
    PROFILE_UNFOLLOW
)


class RoutesTests(TestCase):
    def test_urls_routes(self):
        """Расчеты дают ожидаемые URLs"""
        routes = [
            (CREATE_POST_URL, 'post_create', []),
            ('/', 'main_page', []),
            (GROUP_LIST_URL, 'group_list', [SLUG]),
            (f'/posts/{POST_ID}/', 'post_detail', [POST_ID]),
            (PROFILE_URL, 'profile', [USERNAME]),
            (f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]),
            (POST_COMMENT, 'add_comment', [POST_ID]),
            (FOLLOW_PAGE, 'follow_index', []),
            (PROFILE_FOLLOW, 'profile_follow', [USERNAME]),
            (PROFILE_UNFOLLOW, 'profile_unfollow', [USERNAME])


        ]
        for url, page_name, args in routes:
            with self.subTest(url=url, page=page_name, args=args):
                self.assertEqual(url, reverse('posts:' + page_name, args=args))
