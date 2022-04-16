from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_text = 'Форма создания/редактирования поста'  # added help_text
        help_texts = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Текст нового поста'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'author': 'Автор комментария',
            'text': 'Текст комментария'
        }
