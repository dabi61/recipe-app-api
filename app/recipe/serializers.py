from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer cho nguyên liệu."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer cho thẻ."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer cho công thức nấu ăn"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients'
        ]
        read_only_fields = ['id']

    # ===== VALIDATE RIÊNG LẺ =====
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Tên công thức không được để trống.")
        if len(value) < 3:
            raise serializers.ValidationError("Tên công thức phải có ít nhất 3 ký tự.")
        return value

    def validate_time_minutes(self, value):
        if value <= 0:
            raise serializers.ValidationError("Thời gian nấu phải lớn hơn 0 phút.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Giá tiền không được nhỏ hơn 0.")
        return value

    def validate_link(self, value):
        if value and not value.startswith("http"):
            raise serializers.ValidationError("Đường dẫn không hợp lệ. Phải bắt đầu bằng http hoặc https.")
        return value

    # ===== VALIDATE TỔNG THỂ (TÙY CHỌN) =====
    def validate(self, attrs):
        if not attrs.get('title'):
            raise serializers.ValidationError("Vui lòng nhập tên công thức.")
        return attrs

    # ===== XỬ LÝ TAG / INGREDIENT =====
    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, create = Ingredient.objects.get_or_create(user=auth_user, **ingredient)
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer cho chi tiết công thức."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer cho ảnh công thức."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
