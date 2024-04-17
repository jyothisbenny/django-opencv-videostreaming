from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.models import update_last_login
from .permissions import UserPermissions
from .serializers import UserSerializer
from .filters import UserFilter
from .models import User


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
        queryset = queryset.filter(is_active=True)
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
