from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer cho đối tượng người dùng."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6}
        }

    def validate_email(self, value):
        """Kiểm tra email đã tồn tại hay chưa và đúng định dạng."""
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("Email này đã được sử dụng.")
        if '@' not in value or '.' not in value:
            raise serializers.ValidationError("Email không đúng định dạng.")
        return value.lower().strip()

    def validate_password(self, value):
        """Kiểm tra độ mạnh của mật khẩu."""
        if len(value) < 6:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 6 ký tự.")
        if value.isdigit():
            raise serializers.ValidationError("Mật khẩu không được chỉ là số.")
        return value

    def create(self, validated_data):
        """Tạo và trả về user mới với mật khẩu được mã hóa."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Cập nhật và trả về người dùng."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer cho xác thực người dùng."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        """Xác thực thông tin người dùng."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                {"detail": "Email hoặc mật khẩu không đúng."},
                code='authorization'
            )

        attrs['user'] = user
        return attrs
