from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text')
        labels = {
            'group': _('Группа'),
            'text': _('Текст'),
        }
        help_texts = {
            'group': _('Выберите группу, но это необязательно:)'),
            'text': _('* поле обязательноe для заполнения'),
        }
