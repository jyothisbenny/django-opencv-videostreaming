import django_filters
from .models import User, Video


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'id': ['exact'],
            'name': ['icontains'],
            'email': ['icontains'],
        }


class VideoFilter(django_filters.FilterSet):
    class Meta:
        model = Video
        fields = {
            'id': ['exact'],
            'name': ['icontains'],
            'url': ['iexact', 'icontains'],
        }
