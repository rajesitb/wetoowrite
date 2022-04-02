from django.contrib import admin
from .models import Post, Action, Contact, CommentReply, Comments, PhotoStory, Photo
# Register your models here.


admin.site.register(Comments)
admin.site.register(CommentReply)
admin.site.register(Contact)
admin.site.register(PhotoStory)
admin.site.register(Photo)


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'verb', 'target', 'created')
    list_filter = ('created',)
    search_fields = ('verb',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish')
    list_filter = ('publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'


