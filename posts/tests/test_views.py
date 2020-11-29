
from django import forms
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            description='123',
            slug='test-slug',
            id=1
        )
        cls.group2 = Group.objects.create(
            title='Заголовок2',
            description='1234',
            slug='test-slug2',
            id=2
        )
        cls.user = User.objects.create(username='Marina')
        for _ in range(15):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Текст',
                group=Group.objects.get(slug='test-slug')
            )
        


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

    def test_static_pages_uses_correct_context(self):
        """Шаблоны flatpages сформированы с правильным контекстом."""
        self.static_pages = {
            self.flat_about :'about-author',
            self.flat_tech :'spec'
        }            
        for flat_page, url in self.static_pages.items():
            with self.subTest():
                response = self.guest_client.get(reverse(url))
                response_flat = response.context.get('flatpage')
                self.assertEqual(response_flat.title, flat_page.title)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': (
                reverse('group', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом 
        и с правильным количеством постов"""
        response = self.authorized_client.get(reverse('index'))
        page1 = response.context.get('page')
        page_range = response.context.get('paginator').page_range
        self.assertEqual(len(page1), 10)
        self.assertEqual(len(page_range), 2)


    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,           
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)  

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом 
        и пост попал в нужную группу"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        response_group = response.context.get('group')
        response_group2 = response.context.get('group2')
        self.assertEqual(response_group.title, self.group.title)
        self.assertEqual(response_group.description, self.group.description)
        self.assertEqual(response_group.slug, self.group.slug)
        self.assertIsNone(response_group2, msg=None)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        response_prof = response.context.get('author')
        self.assertEqual(response_prof.username, self.user.username)

    def test_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={
                    'post_id': self.post.id,
                    'username': self.user.username
                }
            )
        )
        response_post = response.context.get('post')
        self.assertEqual(response_post.id, self.post.id)
        self.assertEqual(response_post.author.username, self.user.username)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""    
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'post_id': self.post.id,
                    'username': self.user.username
                }
            )
        )    
        response_post = response.context.get('post')
        self.assertEqual(response_post.id, self.post.id)
        self.assertEqual(response_post.author.username, self.user.username)
