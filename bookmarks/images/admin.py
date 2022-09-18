from django.contrib import admin
from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'image', 'created_at', 'total_likes']
    list_filter = ['created_at']
    ordering = ('-total_likes',)

