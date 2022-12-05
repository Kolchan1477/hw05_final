import shutil
import tempfile

from http import HTTPStatus
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание'
        )

    def test_create_post(self):
        """Проверка создания поста"""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        error_name1 = 'Данные поста не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        text='Текст записанный в форму',
                        group=self.group.id,
                        author=self.user
                        ).exists(), error_name1)
        error_name2 = 'Поcт не добавлен в базу данных'
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         error_name2)
        new_post = Post.objects.last()
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.group, self.group)

    def test_can_edit_post(self):
        """Проверка прав редактирования"""
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        old_text = self.post
        self.group_new = Group.objects.create(title='Тестовая группа_new',
                                              slug='test-group-new',
                                              description='Описание_new')
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group_new.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name1 = 'Данные поста не совпадают'
        self.assertTrue(Post.objects.filter(
                        group=self.group_new.id,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists(), error_name1)

        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0)

        self.authorized_client.post(reverse('posts:add_comment',
                                    kwargs={'post_id': self.post.id}),
                                    {'text': "Тестовый комментарий"},
                                    follow=True)
        response = self.authorized_client.get(f'/posts/{self.post.id}/')
        self.assertContains(response, 'Тестовый комментарий')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_image(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'author': self.user,
            'text': 'Длинный тестовый пост',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                author=self.user,
                text='Длинный тестовый пост',
                image='posts/small.gif',
            ).exists())
