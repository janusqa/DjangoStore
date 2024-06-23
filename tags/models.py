from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# This is a custom query manager to encapsulate getting tags for an object
class TaggedItemManager(models.Manager):
    def get_tags_for(self, object_type, object_id):
        # querying by generic types (tags, likes)
        # 1. find contenttype_id of the object we are interested in
        # 2. use that in conjuction with the object_id to find what we are interested in

        # returns row in content_type table that represents the object, in this case Product
        contenty_type = ContentType.objects.get_for_model(object_type)

        query_set = TaggedItem.objects.select_related("tag").filter(
            content_type=contenty_type,
            object_id=object_id,
        )

        return query_set


# Create your models here.
class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.label}"


# What tag is applied to what object
class TaggedItem(models.Model):
    objects = TaggedItemManager()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
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
        return f"{self.tag} -> {self.content_object}"
