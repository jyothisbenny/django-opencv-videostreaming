import django_filters
from .models import User, Video, Machine, ProductionLog


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


class MachineFilter(django_filters.FilterSet):
    class Meta:
        model = Machine
        fields = {
            'id': ['exact'],
            'machine_name': ['icontains'],
            'machine_serial_no': ['iexact', 'icontains'],
        }


class ProductionLogFilter(django_filters.FilterSet):
    class Meta:
        model = ProductionLog
        fields = {
            'id': ['exact'],
            'cycle_no': ['icontains'],
            'unique_id': ['icontains'],
            'material_name': ['icontains'],
            'start_time': ['exact', 'gte', 'lte'],
            'end_time': ['exact', 'gte', 'lte'],
            'machine': ['exact'],
        }
