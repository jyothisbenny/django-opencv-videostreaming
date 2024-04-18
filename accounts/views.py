import cv2
from datetime import timedelta
from django.utils import timezone
from django.db.models import F
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.models import update_last_login

from .permissions import UserPermissions, VideoPermissions
from .serializers import UserSerializer, VideoSerializer, MachineSerializer, ProductionLogSerializer
from .filters import UserFilter, VideoFilter, MachineFilter, ProductionLogFilter
from .models import User, Video, Machine, ProductionLog
from .services import create_update_record, get_best_stream_url


class UserViewSet(viewsets.ModelViewSet):
    """
    Here we have user login, logout, endpoints.
    """
    queryset = get_user_model().objects.all()
    permission_classes = (UserPermissions,)
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.all()
        self.filterset_class = UserFilter
        queryset = self.filter_queryset(queryset)
        return queryset

    @action(detail=False, methods=['POST'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if email and password:
            # Filter user by email
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                update_last_login(None, user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
            logout(request)
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class VideoViewSet(viewsets.ModelViewSet):
    """
    Here we have video management API's
    """
    queryset = Video.objects.all()
    permission_classes = (VideoPermissions,)
    serializer_class = VideoSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.all()
        self.filterset_class = VideoFilter
        queryset = self.filter_queryset(queryset)
        return queryset

    @action(detail=False, methods=['GET', 'POST', 'PUT'])
    def video_mgmt(self, request):
        if request.method == 'GET':
            queryset = Video.objects.filter(owner=request.user.pk)
            self.filterset_class = VideoFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(VideoSerializer(page, many=True).data, status=status.HTTP_200_OK)
            return Response(VideoSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
        else:
            return Response(create_update_record(request, VideoSerializer, Video))

    @action(detail=False, methods=['GET'])
    def stream(self, request):
        video_id = request.query_params.get('id', None)
        instance = Video.objects.filter(id=video_id).first()
        if not video_id or not instance:
            return Response({'message': 'Invalid Video Id!'}, status=status.HTTP_400_BAD_REQUEST)
        url = instance.url
        best_stream = get_best_stream_url(url)

        def generate_frames():
            cap = cv2.VideoCapture(best_stream)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        response = HttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
        return response

    @action(detail=False, methods=['GET', 'POST', 'PUT'])
    def video_mgmt(self, request):
        if request.method == 'GET':
            queryset = Video.objects.filter(owner=request.user.pk)
            self.filterset_class = VideoFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(VideoSerializer(page, many=True).data, status=status.HTTP_200_OK)
            return Response(VideoSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
        else:
            return Response(create_update_record(request, VideoSerializer, Video))

    @action(detail=False, methods=['GET', 'POST', 'PUT'], serializer_class=MachineSerializer,
            filterset_class=MachineFilter, queryset=Machine)
    def machines(self, request):
        if request.method == 'GET':
            queryset = Machine.objects.filter(is_active=True)
            self.filterset_class = MachineFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(MachineSerializer(page, many=True).data, status=status.HTTP_200_OK)
            return Response(MachineSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
        else:
            return Response(create_update_record(request, MachineSerializer, Machine))

    @action(detail=False, methods=['GET', 'POST', 'PUT'], serializer_class=ProductionLogSerializer,
            filterset_class=ProductionLogFilter, queryset=ProductionLog)
    def production_log(self, request):
        if request.method == 'GET':
            queryset = ProductionLog.objects.filter(is_active=True)
            self.filterset_class = ProductionLogFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(ProductionLogSerializer(page, many=True).data,
                                                   status=status.HTTP_200_OK)
            return Response(ProductionLogSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
        else:
            return Response(create_update_record(request, ProductionLogSerializer, ProductionLog))

    @action(detail=False, methods=['GET'])
    def oee(self, request):
        queryset = ProductionLog.objects.filter(is_active=True)
        self.filterset_class = ProductionLogFilter
        queryset = self.filter_queryset(queryset)

        available_time = 3 * 8
        ideal_cycle_time = 5
        available_operating_time = queryset.count() * ideal_cycle_time
        unplanned_downtime = available_time - available_operating_time
        actual_output = queryset.count()
        duration_queryset = queryset.annotate(duration=F('end_time') - F('start_time'))
        duration_threshold = timedelta(minutes=5)
        good_product = duration_queryset.filter(duration=duration_threshold).distinct().count()
        bad_product = duration_queryset.exclude(duration=duration_threshold).distinct().count()
        total_product = good_product + bad_product

        availability = ((available_time - unplanned_downtime) / available_time) * 100
        performance = ((ideal_cycle_time - actual_output) / available_operating_time) * 100
        quality = (good_product / total_product) * 100
        oee = availability * performance * quality
        return Response({'data': {'oee': oee}}, status=status.HTTP_200_OK)
