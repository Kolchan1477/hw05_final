from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.core.cache import cache
from posts.models import Group, Post
cache.clear()


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def serUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_no_author = Client()
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста'
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )

    def test_urls_guest_client(self):
        """Доступ неавторизированного пользователя"""
        pages = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/'
        )
        for page in pages:
            response = self.guest_client.get(page)
            error_name = f'Ошибка, нет доступа {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_urls_auathorized_client(self):
        """Доступ авторизированного пользователя"""
        pages = ('/create/', f'/posts/{self.post.id}/edit/')
        for page in pages:
            response = self.authorized_client.get(page)
            error_name = f'Ошибка, нет доступа до страницы {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_urls_uses_correct_template(self):
        """Проверка вызываемых шаблонов"""
        cache.clear()
        templates_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for adress, template in templates_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                error_name = f'Ошибка: {adress} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_urls_redirect_guest_client(self):
        """Редирект неавторизованного пользователя"""
        url1 = '/auth/login/?next=/create/'
        url2 = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        pages = {'/create/': url1,
                 f'/posts/{self.post.id}/edit/': url2}
        for page, value in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)

    def test_urls_correct_template_authorised(self):
        """Проверка шаблона у авторизированного пользователя"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_redirect_authorized_but_not_auth(self):
        """Редирект авторизированного пользователя - не автора поста"""
        response = self.authorized_client_no_author.get('/posts/1/edit/',
                                                        follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')
