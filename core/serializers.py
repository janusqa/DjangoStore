from djoser.serializers import UserCreateSerializer, UserSerializer


# !!!NOTE!!! This class must be registered in the settings.py for django to pick it up
# and use it in leiu of djoser's UserCreateSerializer
class CustomCreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        # this class should inherit everything from the UserCreateSerializer's own Meta class
        # Now override the fields attribute which are for the fields we want to add to this
        # serializer
        fields = [
            "pk",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        # this class should inherit everything from the UserCreateSerializer's own Meta class
        # Now override the fields attribute which are for the fields we want to add to this
        # serializer
        fields = [
            "pk",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
