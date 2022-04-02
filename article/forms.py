from django import forms
from django.shortcuts import render
from ckeditor.widgets import CKEditorWidget

from .models import Article, CommentReply, Comments


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'text')


class CommentsForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = Comments
        fields = ('name', 'email', 'body')

    def __init__(self, *args, **kwargs):
        initial_arguments = kwargs.get('initial', None)
        updated_initial = {}
        if initial_arguments:
            user = initial_arguments.get('name', None)#'name' comes from the initial in view.py def post_detai_view
            if user:
                updated_initial['name'] = getattr(user, 'first_name', None)
                updated_initial['email'] = getattr(user, 'email', None)
                kwargs.update(initial=updated_initial)

        super(CommentsForm, self).__init__(*args, **kwargs)

        def com(request):
            if request.GET:
                form = CommentsForm(initial={'user': request.user, 'email': 'give your email'})
                return render(request, 'blog/post_detail.html', {'form': form})


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ('reply',)
        widgets = {
            'name': forms.TextInput(attrs={'required': False, 'autocomplete': False}),
            'reply': forms.TextInput(attrs={'required': False, 'autocomplete': False}),
        }