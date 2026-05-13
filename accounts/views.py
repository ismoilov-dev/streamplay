from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserSerializer, RegisterSerializer, ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


@extend_schema(tags=['auth'])
class RegisterView(generics.CreateAPIView):
    """Yangi foydalanuvchi ro'yxatdan o'tish."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'user': UserSerializer(user).data,
                'message': "Ro'yxatdan muvaffaqiyatli o'tdingiz!",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """Login — JWT token olish (username yoki email bilan)."""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema_view(
    list=extend_schema(tags=['users']),
    retrieve=extend_schema(tags=['users']),
    update=extend_schema(tags=['users']),
    partial_update=extend_schema(tags=['users']),
    destroy=extend_schema(tags=['users']),
    me=extend_schema(tags=['users']),
    change_password=extend_schema(tags=['users']),
)
class UserViewSet(viewsets.ModelViewSet):
    """Foydalanuvchilarni boshqarish."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        """Hozirgi foydalanuvchi profili."""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        # PUT/PATCH
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(request.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """Parolni o'zgartirish."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': "Eski parol noto'g'ri."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': "Parol muvaffaqiyatli o'zgartirildi."})
