from django.contrib import admin

# Register your models here.
from .models import Article, Comments, CommentReply


admin.site.register(Article)
admin.site.register(Comments)
admin.site.register(CommentReply)



