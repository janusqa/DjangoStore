from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings


# Create your models here.
class LikedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Use generic relationship to make this loosley coupled, and it can
    # be used to tagged any type of object. This is done via "ContentTypes"
    # we need:
    # 1. the type of object (content_type) we are tagging,
    # 2. the ID (object_id) of the object being tagged,
    # 3. content_object which retrives the actual object information
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self) -> str:
        return f"{self.content_object} liked by {self.user}"
