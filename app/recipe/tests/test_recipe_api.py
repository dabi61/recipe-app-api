"""
Tests for recipe API
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase #Class dùng để test trong django
from django.urls import reverse #class dùng để lấy url từ tên route trong urls.py

from rest_framework import status
from rest_framework.test import APIClient #giả lập request HTTP như get post push

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list') # Tự động lấy url /api/recipe/recipes

def detail_url(recipe_id):
    """Create and return a recipe detail"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

#Tạo 1 recipe mẫu để dùng cho việc test
def create_recipe(user, **params):
    """Create and a sample recipe"""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal(5.25),
        'description': "Sample description",
        'link': 'https//example.con/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

#Test với người dùng chưa đăng nhập
class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API request.""" 

    def setUp(self):
        self.client = APIClient()

    #Không có auth thì không gọi được api   
    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPES_URL) #Gọi api không kèm theo token

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#Test với người dùng đã đăng nhập
class PrivateRecipeApiTest(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user) # Tự động đăng nhập user này vào model test

    #TH1: Lấy danh sách recipes thành công 
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        #Tạo 2 recipe cho user
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        #Gọi Api get
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        #So sánh dữ liệu của Api trả về với dữ liệu thật trong serializer
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    #Mỗi user chỉ được nhìn thấy recipe của chính mình
    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(email = 'other@example.com',password = 'password123')
        #Tạo 1 recipe cho 1 user khác và tạo 1 recipe cho user đang đăng nhập
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        #Gọi api và đảm bảo chỉ nhìn thấy api của chính mình
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)


        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_get_recipe_detail(self):
        """Test get recipe details"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),    
        }

        #Gửi request post lên recipe url
        res = self.client.post(RECIPES_URL, payload)

        #Kiểm tra trạng thái phản hồi
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        #Lấy recipe mà mình vừa tạo ra (sử dụng chính id của res vừa phản hồi về)
        recipe = Recipe.objects.get(id=res.data['id'])

        #So sánh dữ liệu trong payload với dữ liệu vừa lấy về 
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        #Kiểm tra xem người sở hữu recipe có phải người dùng hiện tại không 
        self.assertEqual(recipe.user, self.user)

    #update recipe with field title
    def test_partial_update(self):
        """Test partial update of a recipe"""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
    
    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description.'
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'new recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    #Không cho thay đổi user recipe bằng một user khác bằng api
    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email = 'user2@example.com', password = 'test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    #Kiểm tra xem người dùng có thể xóa recipe của chính ngta
    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        #204 là status mặc định khi xóa thành công trong res
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    
    #Kiểm tra xem người khác có xóa được recipe của mình không
    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())