from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import tweepy as tw
# for streaming activities
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# get current user
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
# As model field:
from django_currentuser.db.models import CurrentUserField
from taggit.managers import TaggableManager
from django.utils.text import slugify


# will post files to a dir named after the user
def upload_location(post, filename):
    return '%s/%s' % (post.author, filename)


def upload_location_for_comments(comments, filename):
    return '%s/%s' % (comments.post, filename)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post')
    title = models.CharField(max_length=150)
    content = models.TextField()
    allow_comments = models.BooleanField('allow comments', default=True)
    slug = models.SlugField(max_length=150, blank=True)
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    cover = models.ImageField(blank=True, upload_to=upload_location, default='staticfiles/images/logo2.PNG')
    tags = TaggableManager()
    users_like = models.ManyToManyField(User, related_name="users_liked", blank=True)
    total_likes = models.PositiveIntegerField(db_index=True, default=0)
    is_draft = models.BooleanField(default=True, blank=True)
    draft = models.BooleanField(default=True)
    key_point = models.BooleanField(verbose_name='Show key points', default=True)

    class Meta:
        ordering = ("-publish",)

    def __str__(self):
        return f'Post {self.title}, {self.author}'

    def get_absolute_url(self):
        return reverse('post-detail-show', args=[self.pk,
                                                 self.publish.year,
                                                 self.publish.month,
                                                 self.publish.day,
                                                 slugify(self.author.get_full_name()),
                                                 slugify(self.title),
                                                 ])

    def get_full_name(self):
        return slugify(self.author.get_full_name())


class Comments(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post_comment',
                             default=1)
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=150)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class CommentReply(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post_comment_reply',
                             default=1)
    reply = models.CharField(max_length=1050)
    posted_on = models.DateTimeField(auto_now_add=True)
    comments = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name='comments_reply')


class Contact(models.Model):
    user_from = models.ForeignKey("auth.User", related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey("auth.User", related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


# add following fd to users dynamically
User.add_to_class('following', models
                  .ManyToManyField('self', through=Contact,
                                   # otherwise if one user follows another, reverser will
                                   # also be true
                                   related_name='followers', symmetrical=False))


# model to track user activity
class Action(models.Model):
    user = models.ForeignKey('auth.User', related_name='actions',
                             db_index=True, on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    # used to record the target of user action
    target_ct = models.ForeignKey(ContentType, blank=True,
                                  null=True, on_delete=models.CASCADE)
    # limit_choices_to={'model': 'post'})...to limit drop down in admin...not being done now
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    # no record created in the db
    target = GenericForeignKey('target_ct', 'target_id')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Action {self.verb} by {self.user} on {self.created}'


def pic_loc(instance, filename):
    posted_by = get_current_user()
    return '%s/%s' % (posted_by, filename)


class PhotoStory(models.Model):
    story_title = models.CharField(max_length=255, blank=True, default='Title of your Story', null=True)
    slug = models.SlugField(max_length=150, blank=True)
    story_content = models.TextField(blank=True, null=True, default='Write your Story', )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_photo_story')

    def __str__(self):
        return f'Photo {self.story_title} of {self.user}'

    def get_absolute_url(self):
        return reverse('picture-story-view', args=[self.pk,
                                                   self.uploaded_at.year,
                                                   self.uploaded_at.month,
                                                   self.uploaded_at.day,
                                                   slugify(self.user.get_full_name()),
                                                   self.slug,
                                                   ])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.story_title)
        return super(PhotoStory, self).save()

    def get_full_name(self):
        return slugify(self.user.get_full_name())

    class Meta:
        ordering = ['-uploaded_at']


class Photo(models.Model):
    photo_story = models.ForeignKey(PhotoStory, on_delete=models.CASCADE, related_name='story_photo', null=True)
    title_of_the_picture = models.CharField(max_length=255, blank=True, default='Title of the Pic/Video', null=True)
    describe_the_picture = models.CharField(max_length=255, blank=True, null=True, default='Describe the Pic/Video', )
    file = models.FileField(upload_to=pic_loc, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'Photo {self.title_of_the_picture} of {self.photo_story} with {self.file}'

    def get_absolute_url(self):
        return reverse('picture-story-view', args=[self.photo_story.pk,
                                                   self.photo_story.uploaded_at.year,
                                                   self.photo_story.uploaded_at.month,
                                                   self.photo_story.uploaded_at.day,
                                                   slugify(self.photo_story.user.get_full_name()),
                                                   self.photo_story.slug,
                                                   ])

    class Meta:
        ordering = ['-uploaded_at', ]
