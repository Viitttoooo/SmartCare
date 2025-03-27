# This is an auto-generated Django models module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each models has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from enum import Enum
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class IncomeRange(Enum):
    LOW = '小于3000元/月'
    MID = '3000-6000元/月'
    HIGH = '大于6000元/月'


class MaritalStatus(Enum):
    MARRIED = '已婚'
    SINGLE = '未婚'
    DIVORCED = '离婚'
    WIDOWED = '丧偶'
    SEPARATED = '分居'


class Status(Enum):
    PENDING = "待确认"
    SHIPPED = "已预约"
    DELIVERED = "已结束"
    CANCELLED = "已取消"


class PlanStatus(Enum):
    PENDING = "待开始"
    SHIPPED = "进行中"
    DELIVERED = "已完成"


class PlanType(Enum):
    RECOVER = "康复护理"
    DAILY = "日常护理"


class GoalStatus(Enum):
    UNDONE = "未达成"
    DONE = "已达成"


class Type(Enum):
    BREAKFAST = "早餐"
    LUNCH = "午餐"
    DINNER = "晚餐"


class GENDER(Enum):
    MALE = "男"
    FEMALE = "女"


class Appointments(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    client = models.ForeignKey('Clients', models.CASCADE)
    service = models.ForeignKey('Services', models.RESTRICT)
    schedule_date = models.DateField()
    schedule_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    staff = models.ForeignKey('Staff', models.SET_NULL, blank=True, null=True)
    state = models.CharField(
        max_length=3,
        choices=[(tag.value, tag.name) for tag in Status],
        default=Status.PENDING.value,
    )
    satisfaction = models.IntegerField(blank=True, null=True)
    plan = models.ForeignKey('CarePlans', models.CASCADE, blank=True, null=True)


class CarePlans(models.Model):
    plan_id = models.AutoField(primary_key=True)
    client = models.ForeignKey('Clients', models.CASCADE)
    plan_state = models.CharField(
        max_length=3,
        choices=[(tag.value, tag.name) for tag in PlanStatus],
        default=PlanStatus.PENDING.value,
    )
    plan_type = models.CharField(
        max_length=4,
        choices=[(tag.value, tag.name) for tag in PlanType],
        blank=True,
        null=True
    )
    start_date = models.DateField()
    end_date = models.DateField()
    staff = models.ForeignKey('Staff', models.SET_NULL, blank=True, null=True)
    plan_satisfaction = models.IntegerField(blank=True, null=True)


class Clients(models.Model):
    client_id = models.AutoField(primary_key=True, db_comment='客户id')
    user = models.ForeignKey('Users', models.CASCADE)
    care_level = models.IntegerField(blank=True, null=True)
    care_demand = models.CharField(max_length=255, blank=True, null=True)
    medical_history = models.CharField(max_length=255, blank=True, null=True)
    dietary_preference = models.JSONField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name) for tag in GENDER],
        default=GENDER.MALE.value,
    )
    birth_date = models.DateField(blank=True, null=True)
    emergency_contact = models.JSONField(blank=True, null=True)
    marital = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name) for tag in MaritalStatus],
        default=MaritalStatus.SINGLE.value,
    )
    income_range = models.CharField(
        max_length=20,
        choices=[(tag.value, tag.name) for tag in IncomeRange],
        default=IncomeRange.MID.value,
    )


class DietPlans(models.Model):
    diet_plan_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Clients, models.CASCADE)
    diet_date = models.DateField()
    staff = models.ForeignKey('Staff', models.SET_NULL, blank=True, null=True)
    nutrition_requirements = models.JSONField(blank=True, null=True)
    nutrition_taken = models.JSONField(blank=True, null=True)
    smart_recommendation = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('diet_date', 'client')


class FoodRecipes(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    recipe_name = models.CharField(max_length=255)
    nutrition_info = models.JSONField(blank=True, null=True)


class HealthMetrics(models.Model):
    metric_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Clients, models.CASCADE)
    vital_signs = models.JSONField(blank=True, null=True)
    record_date = models.DateTimeField(blank=True, null=True)
    assessment = models.CharField(max_length=1024, blank=True, null=True)
    staff = models.ForeignKey('Staff', models.CASCADE)
    mets_probability = models.FloatField(blank=True, null=True)
    smart_assessment = models.CharField(max_length=1024, blank=True, null=True)


class Ingredients(models.Model):
    ingredient_id = models.AutoField(primary_key=True)
    ingredient_name = models.CharField(max_length=255, unique=True)
    ingredient_description = models.CharField(max_length=255)
    ingredient_amount = models.IntegerField()
    unit = models.CharField(max_length=255)
    nutrition = models.JSONField()


class PlanGoals(models.Model):
    goal_id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(CarePlans, models.CASCADE)
    goal_state = models.CharField(
        max_length=3,
        choices=[(tag.value, tag.name) for tag in GoalStatus],
        default=GoalStatus.UNDONE.value,
    )
    description = models.CharField(max_length=1024, blank=True, null=True)


class PlanRecipe(models.Model):
    diet_plan = models.ForeignKey(DietPlans, models.CASCADE)
    recipe = models.ForeignKey(FoodRecipes, models.CASCADE)
    type = models.CharField(
        max_length=2,
        choices=[(tag.value, tag.name) for tag in Type],
        blank=True,
        null=True
    )


class RecipeIngredient(models.Model):
    id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(FoodRecipes, models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)


class Roles(models.Model):
    role_id = models.IntegerField(primary_key=True)
    role_name = models.CharField(max_length=255)


class Services(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=255)
    duration = models.IntegerField(blank=True, null=True)


# class ShiftRequirements(models.Model):
#     requirement_id = models.AutoField(primary_key=True)
#     template = models.ForeignKey('ShiftTemplates', models.RESTRICT)
#     min_staff = models.CharField(max_length=255)
#     valid_from = models.DateField()
#     valid_to = models.DateField(blank=True, null=True)


class ShiftTemplates(models.Model):
    template_id = models.AutoField(primary_key=True)
    shift_name = models.CharField(max_length=255)
    start_time = models.TimeField()
    end_time = models.TimeField()
    color_code = models.CharField(max_length=255, blank=True, null=True)


class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.CASCADE)


class StaffSchedules(models.Model):
    shift_id = models.AutoField(primary_key=True)
    staff = models.ForeignKey(Staff, models.CASCADE)
    template = models.ForeignKey(ShiftTemplates, models.RESTRICT)
    # week_num = models.IntegerField(blank=True, null=True)
    assigned_date = models.DateField()
    # actual_start = models.DateTimeField()
    # actual_end = models.DateTimeField()

    class Meta:
        unique_together = ('staff', 'assigned_date')


class Users(AbstractUser):
    role = models.ForeignKey(Roles, models.RESTRICT)
    is_reset = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Notification(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']  # 按创建时间降序排列



