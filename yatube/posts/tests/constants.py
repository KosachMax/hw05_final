from django.urls import reverse

POST_ID = 1
SLUG = 'test_slug'
USERNAME = 'auth'
POST_CREATOR = 'post_creator'

REVERSE_INDEX = reverse('posts:main_page')
REVERSE_FOLLOW_INDEX = reverse('posts:follow_index')
REVERSE_POST_CREATE = reverse('posts:post_create')
REVERSE_GROUP_LIST = reverse('posts:group_list', args=[SLUG])
REVERSE_PROFILE = reverse("posts:profile", args=[USERNAME])
REVERSE_PROFILE_FOLLOW = reverse('posts:profile_follow', args=[POST_CREATOR])
REVERSE_PROFILE_UNFOLLOW = reverse(
    'posts:profile_unfollow',
    args=[POST_CREATOR]
)

INDEX_URL_NAME = 'posts:index'
GROUP_LIST_URL_NAME = 'posts:group_list'
PROFILE_URL_NAME = 'posts:profile'
POST_DETAIL_URL_NAME = 'posts:post_detail'
POST_COMMENT_URL_NAME = 'posts:add_comment'
POST_EDIT_URL_NAME = 'posts:post_edit'

INDEX_TEMPLATE = 'posts/index.html'
FOLLOW_TEMPLATE = 'posts/follow.html'
GROUP_LIST_TEMPLATE = 'posts/group_list.html'
PROFILE_TEMPLATE = 'posts/profile.html'
POST_DETAIL_TEMPLATE = 'posts/post_detail.html'
CREATE_POST_TEMPLATE = 'posts/create_post.html'

UNEXISTING_URL = '/unexisting_page/'
ADMIN_PAGE = '/admin/'
CREATE_POST_URL = '/create/'
CREATE_USER_URL = '/auth/login/?next=/create/'
CRT_USER_REDIR_FROM_EDIT_URL = '/auth/login/?next=%2Fposts%2F1%2Fedit%2F'
GROUP_LIST_URL = f'/group/{SLUG}/'
PROFILE_URL = f'/profile/{USERNAME}/'
POST_COMMENT = f'/posts/{POST_ID}/comment/'
FOLLOW_PAGE = '/follow/'
PROFILE_FOLLOW = f'/profile/{USERNAME}/follow/'
PROFILE_UNFOLLOW = f'/profile/{USERNAME}/unfollow/'

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
