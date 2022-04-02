from django import forms
from django.shortcuts import render
import tweepy as tw

from .models import Post, CommentReply, Comments, Contact, Photo, PhotoStory


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'cover', 'tags', 'is_draft', 'key_point']


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
                updated_initial['body'] = 'Please provide a comment!'
                kwargs.update(initial=updated_initial)

        super(CommentsForm, self).__init__(*args, **kwargs)

        def com(request):
            if request.GET:
                form = CommentsForm(initial={'user': request.user, 'email': 'give your email'})
                return render(request, 'blog/post_detail.html', {'form': form})


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ('name', 'reply')
        widgets = {
            'name': forms.TextInput(attrs={'required': False, 'autocomplete': False}),
            'reply': forms.TextInput(attrs={'required': False, 'autocomplete': False}),
        }


def get_trends():
    API_key = 'H6ybab13ZU5cdaUnj6KtP5AMI'
    API_secret = 'VXwYC9cmCnOqVzEpvWonVMqbUBtDX8KiUm40lpIzrz2IadNeeN'
    access_token = '1667776874-rBHAOHpytghmzJUEB7rs6gRi2cqWt3oja9jDF0k'
    access_token_secret = 'TyAztICP2ZU6nEUxgLuGDDmQLVV495YSDW97sRpCnPaYX'
    auth = tw.OAuthHandler(API_key, API_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    trends1 = api.available_trends()
    complete_list = {}
    for i in range(len(trends1)):
        complete_list[trends1[i]['country']] = trends1[i]['woeid']
    selected = dict([(value, key) for key, value in complete_list.items()])
    a = list(selected.items())
    selected_tuple = ()
    for i in range(len(a)):
        selected_tuple = selected_tuple + (a[i],)
    return selected_tuple[1:]


selected = get_trends()


class TrendsForm(forms.Form):
    country = forms.CharField(label="Select a Country to see Trending Tweets",
                              widget=forms.TextInput(
                                  attrs={'onchange': 'this.form.submit()',
                                         'list': 'countries', 'class': 'form-control',
                                         'autocomplete': 'off', 'required': 'false'}))

    def clean(self):
        cleaned_data = super(TrendsForm, self).clean()
        try:
            trends = cleaned_data['country']
        except Exception:
            trends = 'India'
        if not trends:
            raise forms.ValidationError('You have to write something!')
        return trends


class TwitterSearchForm(forms.Form):
    search_twitter = forms.CharField(label='Search Tweets', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Type a trending word here...',
               'onchange': 'this.form.submit()', 'autocomplete': 'off', 'required': 'false'}))


class PhotoForm(forms.ModelForm):
    # file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Photo
        fields = ('title_of_the_picture', 'describe_the_picture', 'file')


class PhotoStoryForm(forms.ModelForm):
    class Meta:
        model = PhotoStory
        fields = ('story_title', 'story_content')




