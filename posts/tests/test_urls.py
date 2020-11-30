
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        site = Site.objects.get(pk=1)
        self.flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='about me',
            content='<b>content</b>'
        )
        self.flat_tech = FlatPage.objects.create(
            url='/about-spec/',
            title='about my tech',
            content='<b>content</b>'
        )
        self.flat_about.sites.add(site)
        self.flat_tech.sites.add(site)
        self.static_pages = ('/about-author/', '/about-spec/')

    def test_static_pages_response(self):
        for url in self.static_pages:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200, f'url: {url}')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Ж'*100,
            slug='test-slug',
        )
        cls.user = User.objects.create(username='Marina')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=Group.objects.get(slug='test-slug')
        )

    def test_pages_url_exists_at_desired_location(self):
        """Проверка доступности /group/test-slug/
        и главной страницы любому пользователю."""
        templates_page_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_urls_exists_at_desired_location_authorized(self):
        """Страницы /new/, /username/, /<username>/<post_id>/
        доступны авторизованному пользователю."""
        templates_page_names = {
            'new.html': reverse('new_post'),
            'profile.html': (
                reverse(
                    'profile',
                    kwargs={
                        'username': self.user.username
                    }
                )
            ),
            'post.html': (
                reverse(
                    'post',
                    kwargs={
                        'post_id': self.post.id,
                        'username': self.user.username
                    }
                )
            )
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Проверяем доступность страницы
        /<username>/<post_id>/edit/ пользователям."""
        template_page_names = {
            'post_edit.html': (
                reverse(
                    'post_edit',
                    kwargs={
                        'post_id': self.post.id,
                        'username': self.user.username,
                    }
                )
            )
        }
        for template, reverse_name in template_page_names.items():
            with self.subTest(template=template):
                response_auth = self.authorized_client.get(reverse_name)
                response_guest = self.guest_client.get(reverse_name)
                self.assertEqual(response_auth.status_code, 200)
                self.assertEqual(response_guest.status_code, 302)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница /<username>/<post_id>/edit/ доступна автору поста."""
        template_page_names = {
            'post_edit.html': (
                reverse(
                    'post_edit',
                    kwargs={
                        'post_id': self.post.id,
                        'username': self.post.author,
                    }
                )
            )
        }
        for template, reverse_name in template_page_names.items():
            with self.subTest(template=template):
                response_auth = self.authorized_client.get(reverse_name)
                self.assertEqual(response_auth.status_code, 200)

    def test_urlы_redirect_anonymous_on_admin_login(self):
        """Страницы /new/ и /<username>/<post_id>/edit/
        перенаправят анонимного пользователя."""
        template_page_names = {
            'post_edit.html': (
                reverse(
                    'post_edit',
                    kwargs={
                        'post_id': self.post.id,
                        'username': self.post.author,
                    }
                )
            ),
            'new_post.html': reverse('new_post')
        }
        for template, reverse_name in template_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': reverse(
                'group',
                kwargs={
                    'slug': self.group.slug
                }
            ),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
