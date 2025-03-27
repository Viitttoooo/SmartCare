from rest_framework import serializers
from .models import Users, Clients, HealthMetrics, CarePlans, Services, Appointments, PlanGoals, ShiftTemplates, Roles, \
    StaffSchedules, Ingredients, FoodRecipes, RecipeIngredient, DietPlans, PlanRecipe, Type, Staff, Notification
from django.db import transaction


# 序列化 Users 模型
class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'role_name', 'is_active', 'is_reset']

    def get_role_name(self, obj):
        return obj.role.role_name if obj.role is not None else ''


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['username', 'first_name', 'last_name', 'email']


class UserShowSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()
    staff_id = serializers.SerializerMethodField()
    client_id = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role_name', 'staff_id', 'client_id']

    def get_role_name(self, obj):
        return obj.role.role_name if obj.role else None

    def get_staff_id(self, obj):
        return Staff.objects.get(user_id=obj.id).staff_id if obj.role.role_name == "员工" else None

    def get_client_id(self, obj):
        return Clients.objects.get(user_id=obj.id).client_id if obj.role.role_name == "客户" else None


# 序列化 登录数据
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)


# 序列化
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)


class AdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Users(**validated_data)
        user.set_password(password)  # 使用 set_password 处理密码哈希
        user.save()
        return user


# 序列化 手机号
class SMSSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=255)


# 序列化 手机号和验证码
class RegisterUserSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=255)
    sms = serializers.CharField(max_length=255)


# 序列化 客户信息
class ClientSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)

    class Meta:
        model = Clients
        fields = "__all__"

    def update(self, instance, validated_data):
        # 移除自动解析的 user 数据
        validated_data.pop("user", None)

        # 更新 Clients 模型的其他字段
        instance = super().update(instance, validated_data)

        # 从原始数据中获取 first_name 和 last_name
        first_name = self.initial_data.get("first_name", None)
        last_name = self.initial_data.get("last_name", None)

        # 如果有更新用户信息，则更新对应的 User 实例
        if first_name is not None or last_name is not None:
            user = instance.user
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            user.save()
        return instance


# 序列化 id
class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


# 序列化 健康档案
class HealthMetricSerializer(serializers.ModelSerializer):
    client_first_name = serializers.SerializerMethodField()
    client_last_name = serializers.SerializerMethodField()
    staff_first_name = serializers.SerializerMethodField()
    staff_last_name = serializers.SerializerMethodField()

    class Meta:
        model = HealthMetrics
        fields = "__all__"

    def get_client_first_name(self, obj):
        return obj.client.user.first_name if obj.client else None

    def get_client_last_name(self, obj):
        return obj.client.user.last_name if obj.client else None

    def get_staff_first_name(self, obj):
        return obj.staff.user.first_name if obj.staff else None

    def get_staff_last_name(self, obj):
        return obj.staff.user.last_name if obj.staff else None


# 序列化 康养计划
class CarePlanSerializer(serializers.ModelSerializer):
    client_first_name = serializers.SerializerMethodField()
    client_last_name = serializers.SerializerMethodField()
    staff_first_name = serializers.SerializerMethodField()
    staff_last_name = serializers.SerializerMethodField()

    class Meta:
        model = CarePlans
        fields = "__all__"

    def get_client_first_name(self, obj):
        return obj.client.user.first_name if obj.client else None

    def get_client_last_name(self, obj):
        return obj.client.user.last_name if obj.client else None

    def get_staff_first_name(self, obj):
        return obj.staff.user.first_name if obj.staff else None

    def get_staff_last_name(self, obj):
        return obj.staff.user.last_name if obj.staff else None


# 序列化 服务
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = "__all__"


# 序列化 预约
class AppointmentSerializer(serializers.ModelSerializer):
    client_first_name = serializers.SerializerMethodField()
    client_last_name = serializers.SerializerMethodField()
    staff_first_name = serializers.SerializerMethodField()
    staff_last_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointments
        fields = "__all__"

    def get_client_first_name(self, obj):
        return obj.client.user.first_name if obj.client else None

    def get_client_last_name(self, obj):
        return obj.client.user.last_name if obj.client else None

    def get_staff_first_name(self, obj):
        return obj.staff.user.first_name if obj.staff else None

    def get_staff_last_name(self, obj):
        return obj.staff.user.last_name if obj.staff else None

    def get_service_name(self, obj):
        return obj.service.service_name if obj.service else None


# 序列化 目标
class PlanGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanGoals
        fields = "__all__"


# 序列化 排班模板
class ShiftTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftTemplates
        fields = "__all__"


# 序列化 角色
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = "__all__"


# 序列化 排班表
class StaffScheduleSerializer(serializers.ModelSerializer):
    staff_first_name = serializers.SerializerMethodField()
    staff_last_name = serializers.SerializerMethodField()

    class Meta:
        model = StaffSchedules
        fields = "__all__"

    def get_staff_first_name(self, obj):
        return obj.staff.user.first_name if obj.staff else None

    def get_staff_last_name(self, obj):
        return obj.staff.user.last_name if obj.staff else None


# 序列化 食材
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = "__all__"


# 序列化 RecipeIngredient，包含食材详情和数量
class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity']


# 序列化 FoodRecipes，包含食材信息
class FoodRecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set', many=True, read_only=True)

    class Meta:
        model = FoodRecipes
        fields = ['recipe_id', 'recipe_name', 'nutrition_info', 'ingredients']


# 用于接收食材输入的序列器
class IngredientInputSerializer(serializers.Serializer):
    ingredient_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField()
    unit = serializers.CharField(max_length=255)


# 用于创建菜谱的序列器
class CreateRecipeSerializer(serializers.Serializer):
    recipe_name = serializers.CharField(max_length=255)
    ingredients = IngredientInputSerializer(many=True)

    def create(self, validated_data):
        with transaction.atomic():
            # 创建菜谱
            recipe = FoodRecipes.objects.create(recipe_name=validated_data['recipe_name'])

            # 初始化营养信息
            total_nutrition = {
                '热量': {'单位': 'kcal', '数量': 0},
                '脂肪': {'单位': 'g', '数量': 0},
                '蛋白质': {'单位': 'g', '数量': 0},
                '碳水化合物': {'单位': 'g', '数量': 0}
            }

            # 处理食材数组
            for ingredient_data in validated_data['ingredients']:
                # 获取食材
                try:
                    ingredient = Ingredients.objects.get(ingredient_name=ingredient_data['ingredient_name'])
                except Ingredients.DoesNotExist:
                    raise serializers.ValidationError(f"食材 {ingredient_data['ingredient_name']} 不存在")

                # 检查单位是否匹配
                if ingredient_data['unit'] != ingredient.unit:
                    raise serializers.ValidationError(
                        f"食材 {ingredient_data['ingredient_name']} 的单位 {ingredient_data['unit']} 与数据库中的单位 {ingredient.unit} 不匹配")

                # 计算份数 (quantity 是用户输入的量，ingredient_amount 是数据库中每份的量)
                quantity = ingredient_data['quantity']
                portions = quantity / ingredient.ingredient_amount

                # 更新营养信息
                for key in total_nutrition:
                    if key in ingredient.nutrition:
                        total_nutrition[key]['数量'] += ingredient.nutrition[key]['数量'] * portions

                # 创建 RecipeIngredient 记录
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=portions  # quantity 表示有多少个 ingredient_amount
                )

            # 保存营养信息
            recipe.nutrition_info = total_nutrition
            recipe.save()
            return recipe


class UpdateRecipeSerializer(serializers.Serializer):
    recipe_id = serializers.IntegerField()
    recipe_name = serializers.CharField(max_length=255, required=False)
    ingredients = IngredientInputSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        with transaction.atomic():
            # 更新菜谱名称（如果提供）
            if 'recipe_name' in validated_data:
                instance.recipe_name = validated_data['recipe_name']

            # 更新食材数组（如果提供）
            if 'ingredients' in validated_data:
                # 删除旧的 RecipeIngredient 记录
                RecipeIngredient.objects.filter(recipe=instance).delete()

                # 初始化新的营养信息
                total_nutrition = {
                    '热量': {'单位': 'kcal', '数量': 0},
                    '脂肪': {'单位': 'g', '数量': 0},
                    '蛋白质': {'单位': 'g', '数量': 0},
                    '碳水化合物': {'单位': 'g', '数量': 0}
                }

                # 处理新的食材数组
                for ingredient_data in validated_data['ingredients']:
                    try:
                        ingredient = Ingredients.objects.get(ingredient_name=ingredient_data['ingredient_name'])
                    except Ingredients.DoesNotExist:
                        raise serializers.ValidationError(f"食材 {ingredient_data['ingredient_name']} 不存在")

                    if ingredient_data['unit'] != ingredient.unit:
                        raise serializers.ValidationError(
                            f"食材 {ingredient_data['ingredient_name']} 的单位 {ingredient_data['unit']} 与数据库中的单位 {ingredient.unit} 不匹配")

                    quantity = ingredient_data['quantity']
                    portions = quantity / ingredient.ingredient_amount

                    for key in total_nutrition:
                        if key in ingredient.nutrition:
                            total_nutrition[key]['数量'] += ingredient.nutrition[key]['数量'] * portions

                    RecipeIngredient.objects.create(
                        recipe=instance,
                        ingredient=ingredient,
                        quantity=portions
                    )

                instance.nutrition_info = total_nutrition

            instance.save()
            return instance


# 膳食计划 序列化
class DietPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlans
        fields = '__all__'


class CertainDayDietPlanSerializer(serializers.ModelSerializer):
    breakfast = serializers.SerializerMethodField()
    lunch = serializers.SerializerMethodField()
    dinner = serializers.SerializerMethodField()

    class Meta:
        model = DietPlans
        fields = ['diet_plan_id', 'client', 'diet_date', 'staff', 'nutrition_requirements', 'smart_recommendation', 'nutrition_taken', 'breakfast', 'lunch', 'dinner']

    def get_breakfast(self, obj):
        recipes = PlanRecipe.objects.filter(diet_plan=obj, type=Type.BREAKFAST.value)
        return [recipe.recipe.recipe_name for recipe in recipes]

    def get_lunch(self, obj):
        recipes = PlanRecipe.objects.filter(diet_plan=obj, type=Type.LUNCH.value)
        return [recipe.recipe.recipe_name for recipe in recipes]

    def get_dinner(self, obj):
        recipes = PlanRecipe.objects.filter(diet_plan=obj, type=Type.DINNER.value)
        return [recipe.recipe.recipe_name for recipe in recipes]


class CreateDietPlanSerializer(serializers.Serializer):
    client_id = serializers.IntegerField()
    diet_date = serializers.DateField()
    type = serializers.ChoiceField(choices=[(tag.value, tag.name) for tag in Type])
    recipe_ids = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        client_id = validated_data['client_id']
        diet_date = validated_data['diet_date']
        meal_type = validated_data['type']
        recipe_ids = validated_data['recipe_ids']

        # 获取或创建当日的膳食计划
        diet_plan, _ = DietPlans.objects.get_or_create(client_id=client_id, diet_date=diet_date)

        # 添加 PlanRecipe 记录
        for recipe_id in recipe_ids:
            recipe = FoodRecipes.objects.get(recipe_id=recipe_id)
            PlanRecipe.objects.create(diet_plan=diet_plan, recipe=recipe, type=meal_type)

        # 计算总营养摄入
        total_nutrition = self.calculate_nutrition(diet_plan)
        diet_plan.nutrition_taken = total_nutrition
        diet_plan.save()
        return diet_plan

    def calculate_nutrition(self, diet_plan):
        all_recipes = PlanRecipe.objects.filter(diet_plan=diet_plan).select_related('recipe')
        total = {
            '热量': {'单位': 'kcal', '数量': 0},
            '脂肪': {'单位': 'g', '数量': 0},
            '蛋白质': {'单位': 'g', '数量': 0},
            '碳水化合物': {'单位': 'g', '数量': 0}
        }
        for plan_recipe in all_recipes:
            nutrition = plan_recipe.recipe.nutrition_info or {}
            for key in total:
                if key in nutrition:
                    total[key]['数量'] += nutrition[key].get('数量', 0)
        return total


class UpdateDietPlanSerializer(serializers.Serializer):
    diet_plan_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=[(tag.value, tag.name) for tag in Type])
    recipe_ids = serializers.ListField(child=serializers.IntegerField())

    def update(self, instance, validated_data):
        meal_type = validated_data['type']
        recipe_ids = validated_data['recipe_ids']

        # 删除该餐次的旧记录
        PlanRecipe.objects.filter(diet_plan=instance, type=meal_type).delete()

        # 添加新记录
        for recipe_id in recipe_ids:
            recipe = FoodRecipes.objects.get(recipe_id=recipe_id)
            PlanRecipe.objects.create(diet_plan=instance, recipe=recipe, type=meal_type)

        # 重新计算总营养摄入
        total_nutrition = self.calculate_nutrition(instance)
        instance.nutrition_taken = total_nutrition
        instance.save()
        return instance

    def calculate_nutrition(self, diet_plan):
        all_recipes = PlanRecipe.objects.filter(diet_plan=diet_plan).select_related('recipe')
        total = {
            '热量': {'单位': 'kcal', '数量': 0},
            '脂肪': {'单位': 'g', '数量': 0},
            '蛋白质': {'单位': 'g', '数量': 0},
            '碳水化合物': {'单位': 'g', '数量': 0}
        }
        for plan_recipe in all_recipes:
            nutrition = plan_recipe.recipe.nutrition_info or {}
            for key in total:
                if key in nutrition:
                    total[key]['数量'] += nutrition[key].get('数量', 0)
        return total


class DeleteDietPlanSerializer(serializers.Serializer):
    diet_plan_id = serializers.IntegerField()
    type = serializers.CharField()


class UpdateDietPlanFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlans
        fields = ['client', 'diet_date', 'staff', 'nutrition_requirements']


class CreateDietPlanRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlans
        fields = ['client', 'diet_date', 'staff', 'nutrition_requirements']


class AvailableStaffSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Staff
        fields = ['staff_id', 'first_name', 'last_name']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'is_read']


class CarePlanWithGoalsSerializer(serializers.ModelSerializer):
    client_first_name = serializers.SerializerMethodField()
    client_last_name = serializers.SerializerMethodField()
    staff_first_name = serializers.SerializerMethodField()
    staff_last_name = serializers.SerializerMethodField()
    goals = PlanGoalSerializer(source='plangoals_set', many=True, read_only=True)

    class Meta:
        model = CarePlans
        fields = [
            'plan_id', 'client', 'plan_state', 'plan_type', 'start_date',
            'end_date', 'staff', 'plan_satisfaction',
            'client_first_name', 'client_last_name',
            'staff_first_name', 'staff_last_name', 'goals'
        ]

    def get_client_first_name(self, obj):
        return obj.client.user.first_name if obj.client else None

    def get_client_last_name(self, obj):
        return obj.client.user.last_name if obj.client else None

    def get_staff_first_name(self, obj):
        return obj.staff.user.first_name if obj.staff else None

    def get_staff_last_name(self, obj):
        return obj.staff.user.last_name if obj.staff else None