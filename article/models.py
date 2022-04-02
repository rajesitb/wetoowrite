from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.urls import reverse
from blog.models import Contact
from ckeditor.fields import RichTextField

# Create your models here.
from django_currentuser.middleware import get_current_user


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_article')
    title = models.CharField(max_length=150)
    text = RichTextUploadingField()
    slug = models.SlugField(max_length=150, blank=True)
    publish = models.DateTimeField(default=timezone.now)
    users_like = models.ManyToManyField(User, related_name="users_liked_article", blank=True)
    total_likes = models.PositiveIntegerField(db_index=True, default=0)
    is_draft = models.BooleanField(default=True, blank=True)
    draft = models.BooleanField(default=True)

    class Meta:
        ordering = ("-publish",)

    def __str__(self):
        return f'Article {self.title} by {self.author}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        return super(Article, self).save()

    def get_absolute_url(self):
        return reverse('article-show-all', args=[self.pk,
                                                 self.slug,
                                                 slugify(self.author.get_full_name()),
                                                 self.publish.year,
                                                 self.publish.month,
                                                 self.publish.day
                                                 ])


class Comments(models.Model):
    article = models.ForeignKey(Article, related_name='comments_article', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=150)
    body = RichTextUploadingField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.article}, {self.id}'

    def get_absolute_url(self):
        return reverse(self.article)


class CommentReply(models.Model):
    name = models.CharField(max_length=100)
    reply = models.CharField(max_length=1050)
    posted_on = models.DateTimeField(auto_now_add=True)
    comments = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name='comments_reply_article')

    def __str__(self):
        return f'Comment reply by {self.name} on {self.comments}, {self.id}'
