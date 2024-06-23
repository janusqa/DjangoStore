from django.contrib import admin
from . import models


class TagAdmin(admin.ModelAdmin):
    search_fields = ["label"]


# Register your models here.
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.TaggedItem)
