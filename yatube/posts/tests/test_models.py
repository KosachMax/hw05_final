from django.test import TestCase

from posts.models import (
    Group,
    Post,
    User,
    Comment,
    Follow
)


class PostModelTest(TestCase):
    CUSTOM_POST_NUM = 15

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Test comment',
        )

    def test_models_have_correct_object_names(self):
        """Проверка корректности работы __str__."""
        field_help_texts = {
            self.post.text[:PostModelTest.CUSTOM_POST_NUM]: str(self.post),
            self.group.title: str(self.group),
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_models_verbose_name(self):
        expected_results = {
            Post: {
                'text': 'Текст поста',
                'author': 'Автор',
                'group': 'Группа',
                'created': 'Дата создания'
            },
            Group: {
                'title': 'Название Группы',
                'slug': 'Уникальный адрес для страницы с группой',
                'description': 'Описание Группы',
            },
            Comment: {
                'post': 'Запись',
                'author': 'Автор коммента',
                'text': 'Текст коммента',
                'created': 'Дата создания'
            },
            Follow: {
                'user': 'Кто Подписывается',
                'author': 'На кого подписывается',
            }
        }
        for model_name, model_values in expected_results.items():
            for verbose_field, verbose_text in model_values.items():
                with self.subTest(model_name=model_name):
                    self.assertEqual(
                        model_name._meta.get_field(
                            verbose_field).verbose_name, verbose_text)

    def test_models_help_text(self):
        expected_results = {
            Post: {
                'text': 'Напишите, о чем сейчас думаете',
                'author': 'Тут указывается автор поста',
                'group': 'Создавайте группы по интересам',
                'created': 'Model unit pub date'
            },
            Group: {
                'title': 'Напишите, как будет называться группа',
                'slug': 'Добавляется автоматически',
                'description': 'Кратко опишите, о чем будет группа',
            },
            Comment: {
                'post': 'Напишите, о чем сейчас думаете',
                'author': 'Тут указывается автор коммента',
                'text': 'Напишите, о чем сейчас думаете',
                'created': 'Model unit pub date'
            },
            Follow: {
                'user': 'Тут указывается кто подписывается',
                'author': 'Тут указывается на кого подписывается'
            }
        }
        for model_name, model_values in expected_results.items():
            for help_field, help_text in model_values.items():
                with self.subTest(model_name=model_name):
                    self.assertEqual(
                        model_name._meta.get_field(
                            help_field).help_text, help_text)
