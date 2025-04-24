"""
View for the recipe APIs
"""
# Là một viewset của DRF tự động cung cấp các hành động
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
# Phương thức xác thực bằng token, Client phải gửi token trong header để
# xác thực
from rest_framework.authentication import TokenAuthentication
# Quyền hạn yêu cầu người dùng phải đăng nhập
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe import serializers

# VD về model viewset
# GET /recipes/ Lấy danh sách recipe
# POST /recipes/: Tạo 1 recipe mới
# GET /recipes/id: Lấy 1 recipe chi tiết
# PUT /recipes/id : update một recipe
# DELETE /recipes/id Delete 1 recipe


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer  # convert data
    queryset = Recipe.objects.all()  # getAll data
    # Chỉ định phương thức xác thực (mỗi request đi kèm với 1 token)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Phải đăng nhập mới vào đuộc

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by(
            '-id')  # Lọc các recipe chỉ thuộc về người dùng hiện tại

    def get_serializer_class(self):
    """Return the serializer class for request."""
    if self.action == 'list':
        return serializers.RecipeSerializer
    elif self.action == 'retrieve':
        return serializers.RecipeDetailSerializer  # ✅ show chi tiết thì dùng detail
    elif self.action == 'upload_image':
        return serializers.RecipeImageSerializer
    return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(instance=recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin, 
                            mixins.ListModelMixin, 
                            viewsets.GenericViewSet):
    """Base viewset for recipe attribute"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

# Mixin những class nhỏ cho phép CRUD nhanh 
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    
    
