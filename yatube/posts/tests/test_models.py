from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверка длины __str__ post"""
        error_name = f'Вывод не имеет {settings.N_OF_POSTS} символов'
        self.assertEqual(self.post.__str__(),
                         self.post.text[:settings.N_OF_POSTS],
                         error_name)

    def test_title_label(self):
        """Проверка заполнения verbose_name"""
        field_verboses = {'text': 'Текст',
                          'pub_date': 'Дата',
                          'group': 'Группа',
                          'author': 'Автор'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value, error_name)

    def test_title_help_text(self):
        """Проверка заполнения help_text"""
        field_help_texts = {'text': 'Введите текст поста',
                            'group': 'Группа, к которой будет относиться пост'
                            }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value, error_name)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_object_name_is_title_field(self):
        """__str__ group - это строчка с содержимым group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
