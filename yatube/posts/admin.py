from django.contrib import admin
from django.conf import settings

from .models import Comment, Follow, Group, Post  # sorted import, added blank line


@admin.register(Post)  # added register decorator
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    list_display_links = ('user', 'author')


admin.site.register(Group)
admin.site.register(Comment)
