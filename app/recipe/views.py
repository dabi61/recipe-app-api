"""
View for the recipe APIs
"""
#Là một viewset của DRF tự động cung cấp các hành động
from rest_framework import viewsets
#Phương thức xác thực bằng token, Client phải gửi token trong header để xác thực
from rest_framework.authentication import TokenAuthentication
#Quyền hạn yêu cầu người dùng phải đăng nhập
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers

#VD về model viewset
#GET /recipes/ Lấy danh sách recipe
#POST /recipes/: Tạo 1 recipe mới
#GET /recipes/id: Lấy 1 recipe chi tiết
#PUT /recipes/id : update một recipe 
#DELETE /recipes/id Delete 1 recipe
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailSerializer # convert data
    queryset = Recipe.objects.all() # getAll data
    authentication_classes = [TokenAuthentication] # Chỉ định phương thức xác thực (mỗi request đi kèm với 1 token)
    permission_classes = [IsAuthenticated] # Phải đăng nhập mới vào đuộc

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id') # Lọc các recipe chỉ thuộc về người dùng hiện tại
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer # Chuyển sang json
        
        return self.serializer_class # Mặc định
    
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)