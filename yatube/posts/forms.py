from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите группу',
            'image': 'Добавьте картинку',
        }
        help_texts = {
            'text': 'Напишите что-нить от души',
            'group': 'В группах одни животные - не удивляйтесь',
            'image': 'Здесь должна быть картинка',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст комментария', }
        help_texts = {'text': 'Напишите Ваш комментарий', }
