
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
            id=1,
        )        
        cls.user = User.objects.create(username='Marina')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=Group.objects.get(slug='test-slug')
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверяем форму создания записи и сохранения ее в базе данных"""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': self.post.text,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        """Проверяем форму редактирования записи и сохранения ее в базе данных"""
        form_data = {
            'group': self.group.id,
            'text': self.post.text,
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                'username': self.user.username,
                'post_id': self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        with self.subTest(
            msg='нет переадресации',
            code=response.status_code
        ):        
            self.assertRedirects(
                response,
                reverse(
                    'post',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                    }
                )
            )
