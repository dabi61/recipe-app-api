from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Tạo người dùng mới trong hệ thống."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Tạo token đăng nhập cho người dùng."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Quản lý người dùng đã xác thực."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Trả về người dùng đã đăng nhập."""
        return self.request.user
