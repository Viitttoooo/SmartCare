from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .cache_keys import CLIENTS_DATA, INGREDIENTS_DATA, PER_CLIENT, STAFF_DATA, PER_METRICS, PER_PLANS, PER_REPORT, \
    PLAN_APPOINTMENTS, PLAN_GOALS, SERVICES_DATA, APPOINTMENTS_DATA, PER_APPOINTMENTS, TEMPLATES_DATA, SCHEDULES_DATA, \
    PER_SCHEDULES, RECIPES_DATA, DIET_PLANS, PER_DIET_PLAN, USERS_DATA, PLANS, ROLES, APPOINTMENTS
from .models import Users, Roles, Clients, GENDER, Staff, HealthMetrics, CarePlans, Services, Appointments, \
    PlanGoals, ShiftTemplates, StaffSchedules, Ingredients, FoodRecipes, RecipeIngredient, DietPlans, PlanRecipe, \
    Notification, MaritalStatus, IncomeRange
from .permissions import IsAdmin, IsStaff, IsClient
from .serializers import UserSerializer, LoginSerializer, SMSSerializer, \
    RegisterUserSerializer, ClientSerializer, IdSerializer, HealthMetricSerializer, CarePlanSerializer, \
    ServiceSerializer, AppointmentSerializer, PlanGoalSerializer, ShiftTemplateSerializer, RoleSerializer, \
    StaffScheduleSerializer, IngredientSerializer, FoodRecipeSerializer, CreateRecipeSerializer, UpdateRecipeSerializer, \
    DietPlanSerializer, CertainDayDietPlanSerializer, CreateDietPlanSerializer, UpdateDietPlanSerializer, \
    DeleteDietPlanSerializer, UpdateDietPlanFieldsSerializer, CreateDietPlanRecordSerializer, UpdateUserSerializer, \
    RegisterSerializer, PasswordSerializer, UserShowSerializer, AvailableStaffSerializer, AdminRegisterSerializer, \
    NotificationSerializer, CarePlanWithGoalsSerializer, AvgSatisfactionSerializer
from django.utils import timezone
from django.contrib.auth import login as django_login
from django.contrib.auth import logout
from datetime import timedelta, datetime
import pytz
from django.core.cache import cache
from .utils import get_diet_recommend, predict_metabolic_syndrome, calculate_age, get_metrics_assessment

appointment_end_line = datetime.strptime("22:00:00", "%H:%M:%S").time()
appointment_start_line = datetime.strptime("09:00:00", "%H:%M:%S").time()

# 定义查询参数
client_id_param = openapi.Parameter(
    name="client_id",
    in_=openapi.IN_QUERY,
    description="客户 ID，例如：1",
    type=openapi.TYPE_INTEGER,
    required=True,
)

diet_date_param = openapi.Parameter(
    name="diet_date",
    in_=openapi.IN_QUERY,
    description="膳食计划日期，格式：YYYY-MM-DD，例如：2023-03-02",
    type=openapi.TYPE_STRING,
    format="date",
    required=True,
)


avoidance_param = openapi.Parameter(
    name="avoidance",
    in_=openapi.IN_QUERY,
    description="逗号分隔的忌口食材，例如：鸡蛋,大蒜",
    type=openapi.TYPE_STRING
)


preference_param = openapi.Parameter(
    name="preference",
    in_=openapi.IN_QUERY,
    description="逗号分隔的爱吃食材，例如：鸡蛋,大蒜",
    type=openapi.TYPE_STRING
)


# 管理员更新用户状态
@swagger_auto_schema(
    method='PATCH'
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_user_active(request, pk):
    user = Users.objects.get(pk=pk)
    if user.role.role_name == "管理员":
        return Response({'error': '不能更改管理员账户状态'}, status=status.HTTP_403_FORBIDDEN)
    user.is_active = not user.is_active
    user.save()
    cache.delete(USERS_DATA)
    serializer = UserSerializer(user)
    return Response(serializer.data)


# 获取所有用户信息
@swagger_auto_schema(
    method='GET',
    operation_description="获取所有用户信息",  # 对接口的描述
    responses={  # 响应描述
        200: '返回所有用户信息'
    }
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def user_list(request):
    users_data = cache.get(USERS_DATA)
    if not users_data:
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        users_data = serializer.data
        cache.set(USERS_DATA, users_data)
    return Response(users_data, status=status.HTTP_200_OK)


# 获取某一用户信息
@swagger_auto_schema(
    method='GET',
    operation_description="获取某一用户的详细信息",  # 对接口的描述
    responses={  # 响应描述
        200: '返回用户的详细信息',
        404: '用户未找到'
    }
)
@api_view(['GET'])
def user_detail(request, pk):
    # 权限验证：只有管理员可以访问此视图
    permission_classes = [IsAdmin]  # 只允许管理员访问

    # 确保用户有权限访问
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        user = Users.objects.get(pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# 获取用户个人信息
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@login_required
def get_user_info(request):
    serializer = UserShowSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 获取所有员工
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@login_required
def get_all_staff(request):
    cache_key = STAFF_DATA
    staff_data = cache.get(cache_key)
    if not staff_data:
        staff = Users.objects.filter(is_staff=True)
        serializer = UserShowSerializer(staff, many=True)
        staff_data = serializer.data
        cache.set(cache_key, staff_data)
    return Response(staff_data, status=status.HTTP_200_OK)


# 密码登录
@swagger_auto_schema(
    method='POST',
    operation_description="用户登录接口",  # 对接口的描述
    request_body=LoginSerializer,  # 请求体使用 LoginSerializer 序列化器
    responses={  # 响应描述
        200: '登录成功，返回用户数据',
        400: '密码错误',
        404: '用户未找到'
    }
)
@api_view(['POST'])
def login(request):
    # 使用序列化器验证请求数据
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            # 查询用户是否存在
            user = Users.objects.get(username=username)

            if not user.is_active:
                return Response({'error': '账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)

            # 检查密码是否匹配
            if check_password(password, user.password):
                # 设置用户会话
                django_login(request, user)  # 这里会使用 Django 的 Session 来记录用户的登录状态 @login_required

                user.last_login = timezone.now()
                user.is_reset = False
                user.save()

                role_name = user.role.role_name

                # 获取用户的数据并返回
                user_data = {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'role_name': role_name,
                    'client_id': Clients.objects.get(user_id=user.id).client_id if role_name == "客户" else None,
                    'staff_id': Staff.objects.get(user_id=user.id).staff_id if role_name == "员工" else None
                }
                return Response(user_data, status=status.HTTP_200_OK)

            else:
                return Response({'error': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        except Users.DoesNotExist:
            return Response({'error': '用户名错误'}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description="用户登出接口",  # 对接口的描述
    responses={  # 响应描述
        200: '登出成功',
        400: '登出失败'
    }
)
@api_view(['POST'])
def user_logout(request):
    """
    用户登出接口，清除当前用户会话。
    """
    try:
        logout(request)  # 清除当前会话，注销用户
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 客户注册接口
@swagger_auto_schema(
    method='POST',
    operation_description="客户注册接口",
    request_body=RegisterSerializer,
    responses={  # 响应描述
        201: '注册成功',
        400: '注册失败',
    }
)
@api_view(['POST'])
def register(request):
    # 使用序列化器验证请求数据
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        date_joined = timezone.now()
        is_active = True
        is_staff = False
        is_superuser = False
        email = serializer.validated_data['email']
        role_id = 1  # 1 表示客户

        # 生成哈希密码
        password_hash = make_password(password)

        if Users.objects.filter(username=username).exists():
            return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建用户
        user = Users.objects.create(
            username=username,
            password=password_hash,
            role_id=role_id,
            first_name=first_name,
            last_name=last_name,
            date_joined=date_joined,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            email=email,
        )

        Clients.objects.create(
            user_id=user.id,
        )
        cache_key = CLIENTS_DATA
        cache.delete(cache_key)
        cache.delete(USERS_DATA)
        # 返回成功响应
        return Response({"message": "registered successfully!"}, status=status.HTTP_200_OK)

    # 如果数据验证失败，返回错误信息
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description="注册任意账号，仅需输入username和密码和role，但也能传入其他参数",
    request_body=AdminRegisterSerializer,
    responses={
        200: "注册成功",
        400: "注册失败"
    }
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def register_admin(request):
    # 检查用户名是否已存在
    username = request.data.get('username')
    if Users.objects.filter(username=username).exists():
        return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查角色是否存在
    try:
        role = Roles.objects.get(pk=request.data['role'])
    except Roles.DoesNotExist:
        return Response({'error': '角色不存在'}, status=status.HTTP_400_BAD_REQUEST)

    # 根据角色设置权限
    is_staff = False
    is_superuser = False
    if role.role_name == "员工":
        is_staff = True
    elif role.role_name == "管理员":
        is_superuser = True

    # 设置默认值
    defaults = {
        'first_name': 'none',
        'last_name': 'none',
        'is_superuser': is_superuser,
        'is_staff': is_staff,
        'is_active': True,
        'date_joined': timezone.now(),
        'email': 'user@example.com',
    }

    # 复制请求数据并补充默认值
    user_data = request.data.copy()
    for key, value in defaults.items():
        if key not in user_data:
            user_data[key] = value

    # 使用序列化器验证和保存
    serializer = AdminRegisterSerializer(data=user_data)
    if serializer.is_valid():
        user = serializer.save()  # 保存到数据库
        cache.delete(USERS_DATA)
        user_id = user.id
        if is_staff:
            Staff.objects.create(user_id=user_id)
        elif not is_staff and not is_superuser:
            Clients.objects.create(user_id=user_id)
            cache_key = CLIENTS_DATA
            cache.delete(cache_key)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 用户个人更新user表中信息
@swagger_auto_schema(
    method='PATCH',
    operation_description="更新用户信息",
    request_body=UpdateUserSerializer,
    responses={
        200: "更新成功",
        400: "更新失败"
    }
)
@api_view(['PATCH'])
@login_required
def edit_user(request):
    user = request.user
    serializer = UpdateUserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员获取reset列表
@swagger_auto_schema(
    method='GET',
)
@api_view(['GET'])
def get_reset_list(request):
    permission_classes = [IsAdmin]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    users = Users.objects.filter(is_reset=True)
    serializer = UserShowSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 用户发出重置密码申请
@swagger_auto_schema(
    method='PATCH'
)
@api_view(['PATCH'])
def put_reset(request, username):
    try:
        user = Users.objects.get(username=username)
    except Users.DoesNotExist:
        return Response({'error': '用户名错误'}, status=status.HTTP_404_NOT_FOUND)

    user.is_reset = True
    user.save()
    cache.delete(USERS_DATA)
    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='PATCH',
    operation_description="管理员重置用户密码",
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def reset_password(request, pk):
    user = Users.objects.get(pk=pk)
    user.password = make_password("123456")
    user.is_reset = False
    user.save()
    cache.delete(USERS_DATA)
    return Response({"message": "password updated successfully!"}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='PATCH'
)
@api_view(['PATCH'])
def reset_deny(request, pk):
    permission_classes = [IsAdmin]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    user = Users.objects.get(pk=pk)
    user.is_reset = False
    user.save()
    return Response(status=status.HTTP_200_OK)


# 用户更新密码
@swagger_auto_schema(
    method='PATCH',
    request_body=PasswordSerializer,
)
@api_view(["PATCH"])
@login_required
def update_password(request):
    user = request.user
    user = Users.objects.get(pk=user.id)
    serializer = PasswordSerializer(data=request.data)
    if serializer.is_valid():
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['password']

        if not check_password(old_password, user.password):
            return Response({"error": "旧密码错误"}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()
    return Response({"message": "password updated successfully!"}, status=status.HTTP_200_OK)


# 查询所有客户信息
@swagger_auto_schema(
    method="GET",
    operation_description="查询所有客户信息",
    responses={
        200: "查询成功",
        400: "查询失败",
    }
)
@api_view(['GET'])
@permission_classes([IsAdmin | IsStaff])
def get_clients(request):
    cache_key = CLIENTS_DATA
    clients_data = cache.get(cache_key)
    if not clients_data:
        # 获取所有客户
        clients = Clients.objects.all()
        serializer = ClientSerializer(clients, many=True)
        clients_data = serializer.data  # 缓存序列化后的数据
        cache.set(cache_key, clients_data)
    return Response(clients_data, status=status.HTTP_200_OK)


# 查询单个客户信息
@swagger_auto_schema(
    method='GET',
    operation_description="查询单个客户信息",
    responses={
        200: "查询成功",
        404: "客户信息不存在"
    }
)
@api_view(['GET'])
@permission_classes([IsAdmin | IsStaff | IsClient])
def get_client_details(request, client_id):
    cache_key = PER_CLIENT.format(client_id)
    client_data = cache.get(cache_key)
    if not client_data:
        try:
            client = Clients.objects.get(client_id=client_id)
            serializer = ClientSerializer(client)
            client_data = serializer.data
            cache.set(cache_key, client_data)
        except Clients.DoesNotExist:
            return Response({"message": "客户信息不存在"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(client_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='PATCH',
    request_body=ClientSerializer,
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdmin | IsStaff | IsClient])
def update_client(request, client_id):
    try:
        # 查找对应的客户对象
        client = Clients.objects.get(client_id=client_id)
    except Clients.DoesNotExist:
        return Response({"error": "客户不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 使用 ClientSerializer 序列化并验证数据
    serializer = ClientSerializer(client, data=request.data, partial=True)

    if serializer.is_valid():
        # 保存更新的数据
        serializer.save()
        cache.delete(CLIENTS_DATA)
        cache.delete(PER_CLIENT.format(client_id))
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        # 如果数据验证失败，返回错误信息
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 员工更新客户个人健康档案
@swagger_auto_schema(
    method='PATCH',
    request_body=HealthMetricSerializer,
    operation_description="员工更新客户个人健康档案",
    responses={
        200: "成功更新",
        400: "更新失败",
        404: "未找到",
    }
)
@api_view(['PATCH'])
@permission_classes([IsStaff | IsAdmin])
def update_client_health_metrics(request):
    data = request.data
    try:
        metric = HealthMetrics.objects.get(metric_id=data['metric_id'])
    except HealthMetrics.DoesNotExist:
        return Response({"error": "该健康档案不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 获取 Clients 实例
    client = metric.client

    # 从 Clients 中提取参数
    age = calculate_age(client.birth_date)
    sex = 'Male' if client.gender == GENDER.MALE.value else 'Female'
    marital_mapping = {
        MaritalStatus.SINGLE.value: 'Single',
        MaritalStatus.MARRIED.value: 'Married',
        MaritalStatus.DIVORCED.value: 'Divorced',
        MaritalStatus.WIDOWED.value: 'Widowed',
        MaritalStatus.SEPARATED.value: 'Separated'
    }
    marital = marital_mapping.get(client.marital, 'Single')
    income_mapping = {
        IncomeRange.LOW.value: 'Low',
        IncomeRange.MID.value: 'Mid',
        IncomeRange.HIGH.value: 'High'
    }
    income_category = income_mapping.get(client.income_range, 'Mid')

    # 获取 vital_signs，若请求中未提供则使用现有值
    vital_signs = data.get('vital_signs', metric.vital_signs)

    # 提取 vital_signs 参数
    waist_circ = vital_signs.get('waist_circumference', {}).get('value')
    bmi = vital_signs.get('bmi', {}).get('value')
    albuminuria_value = vital_signs.get('albuminuria', {}).get('value')
    albuminuria = 1 if albuminuria_value and albuminuria_value > 30 else 0
    ur_alb_cr = vital_signs.get('urine_albumin_creatinine_ratio', {}).get('value')
    uric_acid = vital_signs.get('uric_acid', {}).get('value')
    blood_glucose_mmol_l = vital_signs.get('blood_glucose', {}).get('value')
    hdl_mmol_l = vital_signs.get('hdl_cholesterol', {}).get('value')
    triglycerides_mmol_l = vital_signs.get('triglycerides', {}).get('value')

    # 检查参数完整性
    required_params = [waist_circ, bmi, albuminuria_value, ur_alb_cr, uric_acid, blood_glucose_mmol_l, hdl_mmol_l, triglycerides_mmol_l]
    if any(param is None for param in required_params):
        return Response({"error": "vital_signs 中缺少必要参数"}, status=status.HTTP_400_BAD_REQUEST)

    # 单位转换
    blood_glucose = blood_glucose_mmol_l * 18  # mmol/L -> mg/dL
    hdl = hdl_mmol_l * 38.67  # mmol/L -> mg/dL
    triglycerides = triglycerides_mmol_l * 88.57  # mmol/L -> mg/dL

    # 调用预测工具
    prediction, probability = predict_metabolic_syndrome(
        age=age,
        sex=sex,
        marital=marital,
        income_category=income_category,
        waist_circ=waist_circ,
        bmi=bmi,
        albuminuria=albuminuria,
        ur_alb_cr=ur_alb_cr,
        uric_acid=uric_acid,
        blood_glucose=blood_glucose,
        hdl=hdl,
        triglycerides=triglycerides,
        race='Asian'
    )

    # 将概率添加到 data
    data['mets_probability'] = probability[1]  # probability[1] 为患病概率

    # 更新记录
    serializer = HealthMetricSerializer(metric, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        cache_key = PER_METRICS.format(client.client_id)
        cache.delete(cache_key)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 员工创建客户个人健康档案
@swagger_auto_schema(
    method='POST',
    request_body=HealthMetricSerializer,
    responses={
        200: "成功创建",
        400: "失败",
    }
)
@api_view(['POST'])
@permission_classes([IsStaff | IsAdmin])
def create_client_health_metrics(request):
    data = request.data

    # 获取 Clients 实例
    try:
        client = Clients.objects.get(client_id=data['client'])
    except Clients.DoesNotExist:
        return Response({"error": "该客户不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 从 Clients 中提取参数
    age = calculate_age(client.birth_date)
    sex = 'Male' if client.gender == GENDER.MALE.value else 'Female'
    marital_mapping = {
        MaritalStatus.SINGLE.value: 'Single',
        MaritalStatus.MARRIED.value: 'Married',
        MaritalStatus.DIVORCED.value: 'Divorced',
        MaritalStatus.WIDOWED.value: 'Widowed',
        MaritalStatus.SEPARATED.value: 'Separated'
    }
    marital = marital_mapping.get(client.marital, 'Single')
    income_mapping = {
        IncomeRange.LOW.value: 'Low',
        IncomeRange.MID.value: 'Mid',
        IncomeRange.HIGH.value: 'High'
    }
    income_category = income_mapping.get(client.income_range, 'Mid')

    # 获取 vital_signs
    vital_signs = data.get('vital_signs')

    # 提取 vital_signs 参数
    waist_circ = vital_signs.get('waist_circumference', {}).get('value')
    bmi = vital_signs.get('bmi', {}).get('value')
    albuminuria_value = vital_signs.get('albuminuria', {}).get('value')
    albuminuria = 1 if albuminuria_value and albuminuria_value > 30 else 0
    ur_alb_cr = vital_signs.get('urine_albumin_creatinine_ratio', {}).get('value')
    uric_acid = vital_signs.get('uric_acid', {}).get('value')
    blood_glucose_mmol_l = vital_signs.get('blood_glucose', {}).get('value')
    hdl_mmol_l = vital_signs.get('hdl_cholesterol', {}).get('value')
    triglycerides_mmol_l = vital_signs.get('triglycerides', {}).get('value')

    # 检查参数完整性
    required_params = [waist_circ, bmi, albuminuria_value, ur_alb_cr, uric_acid, blood_glucose_mmol_l, hdl_mmol_l, triglycerides_mmol_l]
    if any(param is None for param in required_params):
        return Response({"error": "vital_signs 中缺少必要参数"}, status=status.HTTP_400_BAD_REQUEST)

    # 单位转换
    blood_glucose = blood_glucose_mmol_l * 18  # mmol/L -> mg/dL
    hdl = hdl_mmol_l * 38.67  # mmol/L -> mg/dL
    triglycerides = triglycerides_mmol_l * 88.57  # mmol/L -> mg/dL

    # 调用预测工具
    prediction, probability = predict_metabolic_syndrome(
        age=age,
        sex=sex,
        marital=marital,
        income_category=income_category,
        waist_circ=waist_circ,
        bmi=bmi,
        albuminuria=albuminuria,
        ur_alb_cr=ur_alb_cr,
        uric_acid=uric_acid,
        blood_glucose=blood_glucose,
        hdl=hdl,
        triglycerides=triglycerides,
        race='Asian'
    )

    # 将概率添加到 data
    data['mets_probability'] = probability[1]  # probability[1] 为患病概率

    # 创建记录
    serializer = HealthMetricSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        cache_key = PER_METRICS.format(client.client_id)
        cache.delete(cache_key)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 查询某客户所有健康档案
@swagger_auto_schema(
    method='GET',
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['GET'])
@permission_classes([IsStaff | IsAdmin | IsClient])
def get_client_health_metrics(request, client_id):
    cache_key = PER_METRICS.format(client_id)
    metrics_data = cache.get(cache_key)
    if not metrics_data:
        try:
            metrics = HealthMetrics.objects.filter(client_id=client_id)
            serializer = HealthMetricSerializer(metrics, many=True)
            metrics_data = serializer.data
            cache.set(cache_key, metrics_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(metrics_data, status=status.HTTP_200_OK)


# 员工删除客户健康档案
@swagger_auto_schema(
    method="DELETE",
)
@api_view(['DELETE'])
@permission_classes([IsStaff | IsAdmin])
def delete_client_health_metrics(request, pk):
    client_id = HealthMetrics.objects.get(pk=pk).client_id
    cache_key = PER_METRICS.format(client_id)
    cache.delete(cache_key)
    HealthMetrics.objects.filter(pk=pk).delete()
    return Response(status=status.HTTP_200_OK)


# 查询客户所有康养计划
@swagger_auto_schema(
    method='GET',
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['GET'])
@permission_classes([IsStaff | IsAdmin | IsClient])
def get_client_plans(request, client_id):
    cache_key = PER_PLANS.format(client_id)
    plans_data = cache.get(cache_key)
    if not plans_data:
        try:
            plans = CarePlans.objects.filter(client_id=client_id)
            serializer = CarePlanSerializer(plans, many=True)
            plans_data = serializer.data
            cache.set(cache_key, plans_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(plans_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="GET",
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(["GET"])
@permission_classes([IsStaff | IsAdmin])
def get_all_appointments(request):
    # 从缓存中获取数据
    data = cache.get(APPOINTMENTS)
    if not data:
        # 查询所有预约数据
        appointments = Appointments.objects.all()
        appointments_serializer = AppointmentSerializer(appointments, many=True)

        # 计算每日满意度均值
        daily_avg = Appointments.objects.filter(satisfaction__isnull=False).annotate(
            date=TruncDay('schedule_date')
        ).values('date').annotate(
            avg_satisfaction=Avg('satisfaction')
        ).order_by('date')

        # 计算月度满意度均值
        monthly_avg = Appointments.objects.filter(satisfaction__isnull=False).annotate(
            month=TruncMonth('schedule_date')
        ).values('month').annotate(
            avg_satisfaction=Avg('satisfaction')
        ).order_by('month')

        # 计算年度满意度均值
        yearly_avg = Appointments.objects.filter(satisfaction__isnull=False).annotate(
            year=TruncYear('schedule_date')
        ).values('year').annotate(
            avg_satisfaction=Avg('satisfaction')
        ).order_by('year')

        # 计算每个服务的满意度均值
        service_avg = Appointments.objects.filter(satisfaction__isnull=False).values('service__service_name').annotate(
            avg_satisfaction=Avg('satisfaction'),
            count=Count('satisfaction')
        ).order_by('service__service_name')

        # 格式化聚合数据
        daily_avg_list = [
            {'date': item['date'].strftime('%Y-%m-%d'), 'avg_satisfaction': round(item['avg_satisfaction'], 2)}
            for item in daily_avg
        ]
        monthly_avg_list = [
            {'month': item['month'].strftime('%Y-%m'), 'avg_satisfaction': round(item['avg_satisfaction'], 2)}
            for item in monthly_avg
        ]
        yearly_avg_list = [
            {'year': item['year'].strftime('%Y'), 'avg_satisfaction': round(item['avg_satisfaction'], 2)}
            for item in yearly_avg
        ]
        service_avg_list = [
            {
                'service_name': item['service__service_name'],
                'avg_satisfaction': round(item['avg_satisfaction'], 2),
                'count': item['count']
            }
            for item in service_avg
        ]

        # 构造返回数据
        data = {
            'appointments': appointments_serializer.data,
            'aggregations': {
                'daily_avg': daily_avg_list,
                'monthly_avg': monthly_avg_list,
                'yearly_avg': yearly_avg_list,
                'service_avg': service_avg_list
            }
        }
        # 将数据存入缓存
        cache.set(APPOINTMENTS, data)

    return Response(data, status=status.HTTP_200_OK)


# 查询所有康复计划及计划包含的目标 用于报表数据展示
@swagger_auto_schema(
    method='GET',
    responses={
        200: openapi.Response(
            description="成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'plans': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    ),
                    'aggregations': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'daily_avg': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                        'avg_satisfaction': openapi.Schema(type=openapi.TYPE_NUMBER)
                                    }
                                )
                            ),
                            'monthly_avg': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'month': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                        'avg_satisfaction': openapi.Schema(type=openapi.TYPE_NUMBER)
                                    }
                                )
                            ),
                            'yearly_avg': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'year': openapi.Schema(type=openapi.TYPE_STRING),
                                        'avg_satisfaction': openapi.Schema(type=openapi.TYPE_NUMBER)
                                    }
                                )
                            )
                        }
                    )
                }
            )
        ),
        403: "Permission denied"
    }
)
@api_view(['GET'])
@permission_classes([IsStaff | IsAdmin])
def get_all_plans(request):
    """
    查询所有康复计划及其包含的目标，用于报表数据展示。
    仅限员工 (IsStaff) 或管理员 (IsAdmin) 访问。
    返回数据包含计划列表和按日、月、年聚合的满意度均值。
    """
    # 获取计划数据（保持原有逻辑）
    data = cache.get(PLANS)
    if not data:
        plans = CarePlans.objects.all().prefetch_related('plangoals_set')
        serializer = CarePlanWithGoalsSerializer(plans, many=True)
        plans_data = serializer.data

        # 计算日、月、年满意度均值
        daily_avg = CarePlans.objects.filter(plan_satisfaction__isnull=False).annotate(
            date=TruncDay('start_date')
        ).values('date').annotate(
            avg_satisfaction=Avg('plan_satisfaction')
        ).order_by('date')

        monthly_avg = CarePlans.objects.filter(plan_satisfaction__isnull=False).annotate(
            month=TruncMonth('start_date')
        ).values('month').annotate(
            avg_satisfaction=Avg('plan_satisfaction')
        ).order_by('month')

        yearly_avg = CarePlans.objects.filter(plan_satisfaction__isnull=False).annotate(
            year=TruncYear('start_date')
        ).values('year').annotate(
            avg_satisfaction=Avg('plan_satisfaction')
        ).order_by('year')

        # 格式化聚合数据
        daily_avg_list = [
            {'date': item['date'].strftime('%Y-%m-%d'), 'avg_satisfaction': round(item['avg_satisfaction'], 2)}
            for item in daily_avg
        ]
        monthly_avg_list = [
            {'month': item['month'].strftime('%Y-%m'), 'avg_satisfaction': round(item['avg_satisfaction'], 2)}
            for item in monthly_avg
        ]
        yearly_avg_list = [
            {'year': item['year'].strftime('%Y'), 'avg_satisfaction': round(item['avg_satisfaction'], 2)}
            for item in yearly_avg
        ]

        # 构建响应数据
        data = {
            'plans': plans_data,
            'aggregations': {
                'daily_avg': daily_avg_list,
                'monthly_avg': monthly_avg_list,
                'yearly_avg': yearly_avg_list
            }
        }
        cache.set(PLANS, data)

    return Response(data, status=status.HTTP_200_OK)


# 创建康复计划
@swagger_auto_schema(
    method='POST',
    request_body=CarePlanSerializer,
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['POST'])
@permission_classes([IsStaff | IsAdmin])
def create_care_plans(request):
    data = request.data
    if 'plan_satisfaction' in data:
        del data['plan_satisfaction']

    if request.user.is_staff:
        data['staff'] = Staff.objects.get(user_id=request.user.id).staff_id

    if data.get('end_date') and data.get('start_date') and data['end_date'] < data['start_date']:
        return Response({'error': '结束日期必须大于等于开始日期'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CarePlanSerializer(data=data)
    if serializer.is_valid():
        try:
            serializer.save()
            client_id = data['client']
            cache_key = PER_PLANS.format(client_id)
            cache.delete(cache_key)
            cache.delete(PLANS)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 删除康养计划
@swagger_auto_schema(
    method="DELETE",
)
@api_view(["DELETE"])
@permission_classes([IsStaff | IsAdmin])
def delete_care_plans(request, pk):
    try:
        plan = CarePlans.objects.get(pk=pk)
        client_id = plan.client_id
        plan.delete()
        cache_key = PER_PLANS.format(client_id)
        cache.delete(cache_key)
        cache.delete(PLANS)
        return Response({'msg': 'delete successfully'}, status=status.HTTP_200_OK)
    except CarePlans.DoesNotExist:
        return Response({'message': "FINE"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 更新康复计划
@swagger_auto_schema(
    method='PATCH',
    request_body=CarePlanSerializer,
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['PATCH'])
@permission_classes([IsStaff | IsAdmin])
def update_care_plans(request):

    data = request.data
    if request.user.is_staff:
        data['staff'] = Staff.objects.get(user_id=request.user.id).staff_id

    if 'plan_satisfaction' in data:
        del data['plan_satisfaction']

    try:
        plan_id = data['plan_id']
        plan = CarePlans.objects.get(plan_id=plan_id)

        if 'end_date' in data:
            end_date = data['end_date']
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = plan.end_date

        if 'start_date' in data:
            start_date = data['start_date']
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = plan.start_date

        if start_date > end_date:
            return Response({'error': '结束日期必须大于等于开始日期'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CarePlanSerializer(plan, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            client_id = plan.client_id
            cache.delete(PER_PLANS.format(client_id))
            cache.delete(PER_REPORT.format(plan_id))
            cache.delete(PLANS)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 查询所有服务
@swagger_auto_schema(
    method='GET',
    operation_description="查询所有服务",
    responses={
        200: "成功",
        400: "失败"
    }
)
@api_view(['GET'])
@login_required
def get_services(request):
    cache_key = SERVICES_DATA
    services_data = cache.get(cache_key)
    if not services_data:
        services = Services.objects.all()
        serializer = ServiceSerializer(services, many=True)
        services_data = serializer.data
        cache.set(cache_key, services_data)
    return Response(services_data, status=status.HTTP_200_OK)


# 新增服务
@swagger_auto_schema(
    method="POST",
    operation_description="新增服务",
    request_body=ServiceSerializer,
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['POST'])
@permission_classes([IsStaff | IsAdmin])
def create_service(request):
    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        cache.delete(SERVICES_DATA)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 更新服务
@swagger_auto_schema(
    method='PATCH',
    request_body=ServiceSerializer,
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['PATCH'])
@permission_classes([IsStaff | IsAdmin])
def update_service(request):
    try:
        service = Services.objects.get(pk=request.data['service_id'])
    except Services.DoesNotExist:
        return Response({'error': '该服务不存在'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ServiceSerializer(service, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        cache.delete(SERVICES_DATA)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 删除服务
@swagger_auto_schema(
    method='DELETE',
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(['DELETE'])
@permission_classes([IsStaff | IsAdmin])
def delete_service(request, pk):
    Services.objects.filter(pk=pk).delete()
    cache.delete(SERVICES_DATA)
    return Response({'msg': "Deleted successfully"}, status=status.HTTP_200_OK)


# 查询所有预约
@swagger_auto_schema(
    method="GET",
    responses={
        200: "成功",
        400: "失败",
    }
)
@api_view(["GET"])
@permission_classes([IsStaff | IsAdmin])
def get_appointments(request):
    appointments_data = cache.get(APPOINTMENTS_DATA)
    if not appointments_data:
        appointments = Appointments.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        appointments_data = serializer.data
        cache.set(APPOINTMENTS_DATA, appointments_data)
    return Response(appointments_data, status=status.HTTP_200_OK)


# 删除对应预约
@swagger_auto_schema(
    method="DELETE",
)
@api_view(["DELETE"])
@permission_classes([IsStaff | IsAdmin])
def delete_appointments(request, pk):
    try:
        appointment = Appointments.objects.get(pk=pk)
        plan_id = appointment.plan_id
        client_id = appointment.client_id
        appointment.delete()
        cache.delete(PER_REPORT.format(plan_id))
        cache.delete(PLAN_APPOINTMENTS.format(plan_id))
        cache.delete(APPOINTMENTS_DATA)
        cache.delete(APPOINTMENTS)
        cache.delete(PER_APPOINTMENTS.format(client_id))
        return Response(status=status.HTTP_200_OK)
    except Appointments.DoesNotExist:
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 查询某一客户的所有预约
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@permission_classes([IsStaff | IsAdmin | IsClient])
def get_client_appointments(request, client_id):
    appointments_data = cache.get(PER_APPOINTMENTS.format(client_id))
    if not appointments_data:
        appointments = Appointments.objects.filter(client_id=client_id)
        serializer = AppointmentSerializer(appointments, many=True)
        appointments_data = serializer.data
        cache.set(PER_APPOINTMENTS.format(client_id), appointments_data)
    return Response(appointments_data, status=status.HTTP_200_OK)


# 添加预约
@swagger_auto_schema(
    method="POST",
    request_body=AppointmentSerializer,
)
@api_view(["POST"])
@permission_classes([IsStaff | IsAdmin | IsClient])
def create_appointment(request, client_id):

    data = request.data
    data["client"] = client_id

    if 'satisfaction' in data:
        del data['satisfaction']


    # 获取服务时长（单位分钟）
    duration = Services.objects.get(pk=data["service"]).duration

    # 获取预约的 schedule_time 和 end_time（如果有）
    schedule_time = data.get("schedule_time")
    schedule_date = data.get("schedule_date")

    # 将字符串转换为 date 类型和 time 类型
    schedule_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    schedule_time = datetime.strptime(schedule_time, "%H:%M:%S").time()

    schedule_datetime = datetime.combine(schedule_date, schedule_time)

    end_time = schedule_datetime + timedelta(minutes=duration)

    # 检查 end_time 是否超过22:00
    if end_time > datetime.combine(schedule_date, appointment_end_line):
        return Response({'error': f'预约结束时间不能晚于 {str(appointment_end_line)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    if schedule_time < appointment_start_line:
        return Response({'error': f'预约时间不能早于 {str(appointment_start_line)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        if data.get('plan') and CarePlans.objects.get(pk=data["plan"]).client_id != client_id:
            return Response({'error': "客户id不匹配"}, status=status.HTTP_400_BAD_REQUEST)
    except CarePlans.DoesNotExist:
        return Response({'error': "康复计划不存在"}, status=status.HTTP_400_BAD_REQUEST)

    # 检查客户是否有时间冲突
    existing_appointments = Appointments.objects.filter(client_id=client_id).exclude(pk=data.get('appointment_id', None)).exclude(state__in=["已取消", "已结束"])
    for appointment in existing_appointments:
        existing_start_time = datetime.combine(appointment.schedule_date, appointment.schedule_time)
        existing_end_time = existing_start_time + timedelta(minutes=appointment.service.duration)

        # 检查是否有时间冲突（不包括端点重合）
        if (schedule_datetime < existing_end_time) and (end_time > existing_start_time):
            return Response({'error': '客户在该时间段已有预约'}, status=status.HTTP_400_BAD_REQUEST)

    staff_id = data.get('staff')
    # 检查员工是否有时间冲突 且 有排班
    if staff_id:
        # 检查员工是否有排班
        staff_schedule = StaffSchedules.objects.filter(staff_id=staff_id, assigned_date=schedule_date).first()
        if not staff_schedule:
            return Response({'error': '员工在该日期没有排班'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取排班模板中的开始和结束时间
        shift_template = staff_schedule.template
        shift_start_time = shift_template.start_time
        shift_end_time = shift_template.end_time

        # 组合成 datetime 对象
        shift_start_datetime = datetime.combine(schedule_date, shift_start_time)
        shift_end_datetime = datetime.combine(schedule_date, shift_end_time)

        # 检查预约时间是否在排班时间内
        if not (shift_start_datetime <= schedule_datetime and end_time <= shift_end_datetime):
            return Response({'error': '预约时间不在员工的排班时间内'}, status=status.HTTP_400_BAD_REQUEST)


        staff_appointments = Appointments.objects.filter(staff_id=staff_id).exclude(pk=data.get('appointment_id', None)).exclude(state__in=["已取消", "已结束"])
        for appointment in staff_appointments:
            existing_start_time = datetime.combine(appointment.schedule_date, appointment.schedule_time)
            existing_end_time = existing_start_time + timedelta(minutes=appointment.service.duration)

            # 检查是否有时间冲突（不包括端点重合）
            if (schedule_datetime < existing_end_time) and (end_time > existing_start_time):
                return Response({'error': '员工在该时间段已有预约'}, status=status.HTTP_400_BAD_REQUEST)

    # 如果检查通过，保存预约
    data["end_time"] = end_time.time()
    serializer = AppointmentSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        if 'plan' in data:
            cache.delete(PLAN_APPOINTMENTS.format(request.data['plan']))
            cache.delete(PER_REPORT.format(request.data['plan']))
        cache.delete(APPOINTMENTS_DATA)
        cache.delete(APPOINTMENTS)
        cache.delete(PER_APPOINTMENTS.format(client_id))
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 更新预约
@swagger_auto_schema(
    method="PATCH",
    request_body=AppointmentSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsStaff | IsAdmin | IsClient])
def update_appointment(request, client_id):
    appointment_id = request.data.get('appointment_id')

    try:
        appointment = Appointments.objects.get(appointment_id=appointment_id)
    except Appointments.DoesNotExist:
        return Response({'error': '无该预约'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    is_edit = False
    plan_id = appointment.plan_id


    # 如果更新了 service_id，则需要获取新的服务时长
    if "service" in data:
        new_service = Services.objects.get(pk=data["service"])
        duration = new_service.duration
        is_edit = True
    else:
        duration = appointment.service.duration  # 如果没有更新service，保持原来的时长

    if "schedule_date" in data:
        schedule_date = data["schedule_date"]
        schedule_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
        is_edit = True
    else:
        schedule_date = appointment.schedule_date

    # 更新预约时间
    if "schedule_time" in data:
        schedule_time = data["schedule_time"]
        schedule_time = datetime.strptime(schedule_time, "%H:%M:%S").time()
        is_edit = True
    else:
        schedule_time = appointment.schedule_time

    schedule_datetime = datetime.combine(schedule_date, schedule_time)
    end_time = schedule_datetime + timedelta(minutes=duration)

    # 检查 end_time 是否超过22:00
    if end_time > datetime.combine(schedule_date, appointment_end_line):
        return Response({'error': f'预约结束时间不能晚于 {str(appointment_end_line)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    if schedule_time < appointment_start_line:
        return Response({'error': f'预约开始时间不能早于 {str(appointment_start_line)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    if "staff" in data:
        staff_id = data["staff"]
        is_edit = True
    else:
        staff_id = appointment.staff_id

    try:
        if data.get('plan') and CarePlans.objects.get(pk=data["plan"]).client_id != client_id:
            return Response({'error': "客户id不匹配"}, status=status.HTTP_400_BAD_REQUEST)
    except CarePlans.DoesNotExist:
        return Response({'error': "该康复计划不存在"}, status=status.HTTP_400_BAD_REQUEST)

    if is_edit:
        # 检查客户是否有时间冲突
        existing_appointments = Appointments.objects.filter(client_id=client_id).exclude(pk=data.get('appointment_id', None)).exclude(state__in=["已取消", "已结束"])
        for e_appointment in existing_appointments:
            existing_start_time = datetime.combine(e_appointment.schedule_date, e_appointment.schedule_time)
            existing_end_time = existing_start_time + timedelta(minutes=e_appointment.service.duration)

            # 检查是否有时间冲突（不包括端点重合）
            if (schedule_datetime < existing_end_time) and (end_time > existing_start_time):
                return Response({'error': '客户在该时间段已有预约'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查员工是否有时间冲突
        if staff_id:
            # 检查员工是否有排班
            staff_schedule = StaffSchedules.objects.filter(staff_id=staff_id, assigned_date=schedule_date).first()
            if not staff_schedule:
                return Response({'error': '员工在该日期没有排班'}, status=status.HTTP_400_BAD_REQUEST)

            # 获取排班模板中的开始和结束时间
            shift_template = staff_schedule.template
            shift_start_time = shift_template.start_time
            shift_end_time = shift_template.end_time

            # 组合成 datetime 对象
            shift_start_datetime = datetime.combine(schedule_date, shift_start_time)
            shift_end_datetime = datetime.combine(schedule_date, shift_end_time)

            # 检查预约时间是否在排班时间内
            if not (shift_start_datetime <= schedule_datetime and end_time <= shift_end_datetime):
                return Response({'error': '预约时间不在员工的排班时间内'}, status=status.HTTP_400_BAD_REQUEST)

            staff_appointments = Appointments.objects.filter(staff_id=staff_id).exclude(pk=data.get('appointment_id', None)).exclude(state__in=["已取消", "已结束"])
            for s_appointment in staff_appointments:
                existing_start_time = datetime.combine(s_appointment.schedule_date, s_appointment.schedule_time)
                existing_end_time = existing_start_time + timedelta(minutes=s_appointment.service.duration)

                # 检查是否有时间冲突（不包括端点重合）
                if (schedule_datetime < existing_end_time) and (end_time > existing_start_time):
                    return Response({'error': '员工在该时间段已有预约'}, status=status.HTTP_400_BAD_REQUEST)

    data["end_time"] = end_time.time()
    serializer = AppointmentSerializer(appointment, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        cache.delete(PLAN_APPOINTMENTS.format(plan_id))
        cache.delete(PER_REPORT.format(plan_id))
        cache.delete(APPOINTMENTS_DATA)
        cache.delete(APPOINTMENTS)
        cache.delete(PER_APPOINTMENTS.format(client_id))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 新建目标
@swagger_auto_schema(
    method="POST",
    request_body=PlanGoalSerializer,
    responses={
        200: "成功",
        400: "失败"
    }
)
@api_view(["POST"])
@permission_classes([IsStaff | IsAdmin])
def create_goal(request):
    serializer = PlanGoalSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        plan_id = request.data['plan']
        cache_key = PLAN_GOALS.format(plan_id)
        cache.delete(cache_key)
        cache.delete(PER_REPORT.format(plan_id))
        cache.delete(PLANS)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 更新目标
@swagger_auto_schema(
    method="PATCH",
    request_body=PlanGoalSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsStaff | IsAdmin])
def update_goal(request):
    goal = PlanGoals.objects.get(pk=request.data["goal_id"])
    serializer = PlanGoalSerializer(goal, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        plan_id = goal.plan_id
        cache_key = PLAN_GOALS.format(plan_id)
        cache.delete(cache_key)
        cache.delete(PER_REPORT.format(plan_id))
        cache.delete(PLANS)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 删除goal
@swagger_auto_schema(
    method="DELETE",
)
@api_view(["DELETE"])
@permission_classes([IsStaff | IsAdmin])
def delete_goal(request, pk):
    try:
        goal = PlanGoals.objects.get(pk=pk)
        plan_id = goal.plan_id
        goal.delete()
        cache_key = PLAN_GOALS.format(plan_id)
        cache.delete(cache_key)
        cache.delete(PER_REPORT.format(plan_id))
        cache.delete(PLANS)
        return Response({'msg': "success"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 查询康复计划包含的预约
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@login_required
def get_plan_appointments(request, plan_id):
    cache_key = PLAN_APPOINTMENTS.format(plan_id)
    appointments = cache.get(cache_key)
    if not appointments:
        appointments = Appointments.objects.filter(plan_id=plan_id)
        serializer = AppointmentSerializer(appointments, many=True)
        appointments = serializer.data
        cache.set(cache_key, appointments)
    return Response(appointments, status=status.HTTP_200_OK)


# 查询康复计划包含的目标
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@login_required
def get_plan_goals(request, plan_id):
    cache_key = PLAN_GOALS.format(plan_id)
    goals = cache.get(cache_key)
    if not goals:
        goals = PlanGoals.objects.filter(plan_id=plan_id)
        serializer = PlanGoalSerializer(goals, many=True)
        goals = serializer.data
        cache.set(cache_key, goals)
    return Response(goals, status=status.HTTP_200_OK)


# 客户为康复计划评分
@swagger_auto_schema(
    method="PATCH",
    request_body=CarePlanSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsClient])
def score_plan(request, client_id):
    # 验证是否为当前客户的计划
    try:
        plan = CarePlans.objects.get(pk=request.data["plan_id"])
    except CarePlans.DoesNotExist:
        return Response({'error': '无此护理计划'}, status=status.HTTP_400_BAD_REQUEST)
    if plan.client_id != client_id:
        return Response({'error': "客户id不匹配"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        plan.plan_satisfaction = request.data['plan_satisfaction']
        plan.save()
        serializer = CarePlanSerializer(plan)
        cache.delete(PLANS)
        cache.delete(PER_PLANS.format(plan.client_id))
        cache.delete(PER_REPORT.format(plan.plan_id))
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 获取康复计划进度报告
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@login_required
def get_plan_progress(request, plan_id):
    cache_key = PER_REPORT.format(plan_id)
    report_data = cache.get(cache_key)
    if not report_data:
        try:
            # 获取康复计划
            plan = CarePlans.objects.get(pk=plan_id)
        except CarePlans.DoesNotExist:
            return Response({'error': '无此护理计划'}, status=status.HTTP_400_BAD_REQUEST)

        # 序列化 CarePlan 数据
        serializer = CarePlanSerializer(plan)

        # 获取目标状态并统计“未达成”和“已达成”的数量
        goal_undone = PlanGoals.objects.filter(plan_id=plan_id, goal_state="未达成").count() or 0
        goal_done = PlanGoals.objects.filter(plan_id=plan_id, goal_state="已达成").count() or 0

        # 获取预约状态并统计四种状态的数量
        appointment_pending = Appointments.objects.filter(plan_id=plan_id, state="待确认").count() or 0
        appointment_booked = Appointments.objects.filter(plan_id=plan_id, state="已预约").count() or 0
        appointment_ended = Appointments.objects.filter(plan_id=plan_id, state="已结束").count() or 0
        appointment_cancelled = Appointments.objects.filter(plan_id=plan_id, state="已取消").count() or 0

        # 获取当前北京时间
        tz = pytz.timezone('Asia/Shanghai')
        today = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        report_data = {
            'care_plan': serializer.data,
            'goal_undone': goal_undone,
            'goal_done': goal_done,
            'appointment_pending': appointment_pending,
            'appointment_booked': appointment_booked,
            'appointment_ended': appointment_ended,
            'appointment_cancelled': appointment_cancelled,
            'today': today
        }
        cache.set(cache_key, report_data)
    return Response(report_data, status=status.HTTP_200_OK)


# 管理员添加排班模板
@swagger_auto_schema(
    method="POST",
    request_body=ShiftTemplateSerializer,
)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_shift_template(request):
    serializer = ShiftTemplateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        cache.delete(TEMPLATES_DATA)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员修改排班模板
@swagger_auto_schema(
    method="PATCH",
    request_body=ShiftTemplateSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_shift_template(request):
    template_id = request.data["template_id"]
    template = ShiftTemplates.objects.get(pk=template_id)
    serializer = ShiftTemplateSerializer(template, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        cache.delete(TEMPLATES_DATA)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员删除排班模板
@swagger_auto_schema(
    method="DELETE",
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_shift_template(request, pk):
    ShiftTemplates.objects.filter(pk=pk).delete()
    cache.delete(TEMPLATES_DATA)
    return Response({'msg': 'delete success'}, status=status.HTTP_200_OK)


# 员工或管理员查询排班模板
@swagger_auto_schema(
    method='GET'
)
@api_view(["GET"])
@permission_classes([IsAdmin | IsStaff])
def get_shift_template(request):
    templates_data = cache.get(TEMPLATES_DATA)
    if not templates_data:
        templates = ShiftTemplates.objects.all()
        serializer = ShiftTemplateSerializer(templates, many=True)
        templates_data = serializer.data
        cache.set(TEMPLATES_DATA, templates_data)
    return Response(templates_data, status=status.HTTP_200_OK)


# 管理员添加角色
@swagger_auto_schema(
    method="POST",
    request_body=RoleSerializer,
)
@api_view(["POST"])
def create_role(request):
    permission_classes = [IsAdmin]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    serializer = RoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员修改角色
@swagger_auto_schema(
    method="PATCH",
    request_body=RoleSerializer,
)
@api_view(["PATCH"])
def update_role(request):
    permission_classes = [IsAdmin]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    role = Roles.objects.get(pk=request.data["role_id"])
    serializer = RoleSerializer(role, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员查看角色
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@permission_classes([IsAdmin])
def get_role(request):
    roles_data = cache.get(ROLES)
    if not roles_data:
        roles = Roles.objects.all()
        serializer = RoleSerializer(roles, many=True)
        roles_data = serializer.data
        cache.set(ROLES, roles_data)
    return Response(roles_data, status=status.HTTP_200_OK)


# 管理员新增排班
@swagger_auto_schema(
    method="POST",
    request_body=StaffScheduleSerializer,
)
@api_view(["POST"])
@permission_classes([IsAdmin])
def create_staff_schedule(request):
    serializer = StaffScheduleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        cache.delete(SCHEDULES_DATA)
        cache.delete(PER_SCHEDULES.format(request.data['staff']))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(
        {'error': "员工在该日期已有排班" if 'unique' in str(serializer.errors) else str(serializer.errors)},
        status=status.HTTP_400_BAD_REQUEST)


# 管理员修改排班，如果员工在排班期间有预约那么这些预约的负责员工全部置为null
@swagger_auto_schema(
    method="PATCH",
    request_body=StaffScheduleSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdmin])
def update_staff_schedule(request):
    # 获取要更新的排班记录
    shift_id = request.data.get("shift_id")
    try:
        schedule = StaffSchedules.objects.get(pk=shift_id)
    except StaffSchedules.DoesNotExist:
        return Response({'error': '排班记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 获取更新前的原始数据
    original_assigned_date = schedule.assigned_date
    original_template = schedule.template
    original_staff_id = schedule.staff_id

    # 使用序列化器验证并更新数据
    serializer = StaffScheduleSerializer(schedule, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
            {'error': "员工在该日期已有排班" if 'unique' in str(serializer.errors) else str(serializer.errors)},
            status=status.HTTP_400_BAD_REQUEST)

    # 获取更新后的数据
    updated_data = serializer.validated_data
    new_assigned_date = updated_data.get('assigned_date', original_assigned_date)
    new_template = updated_data.get('template', original_template)
    new_staff_id = updated_data.get('staff_id', original_staff_id)

    # 保存更新后的排班数据
    serializer.save()
    cache.delete(SCHEDULES_DATA)
    cache.delete(PER_SCHEDULES.format(original_staff_id))
    cache.delete(PER_SCHEDULES.format(new_staff_id))

    # 如果排班日期或模板（时间段）发生变化，更新相关预约
    if original_assigned_date != new_assigned_date or original_template != new_template:
        # 获取原排班的开始和结束时间
        original_start_time = original_template.start_time
        original_end_time = original_template.end_time

        # 查找员工在原排班日期和时间段内的所有未取消和未结束的预约
        appointments_to_update = Appointments.objects.filter(
            staff=schedule.staff,
            schedule_date=original_assigned_date,
            schedule_time__gte=original_start_time,
            schedule_time__lt=original_end_time
        ).exclude(state__in=["已取消", "已结束"])

        count = appointments_to_update.count()
        client_ids = list(appointments_to_update.values_list('client', flat=True).distinct().order_by('client'))

        # 将这些预约的 staff 字段设为 null
        appointments_to_update.update(staff=None)

        if count:
            cache.delete(APPOINTMENTS_DATA)
            cache.delete(APPOINTMENTS)
            for client_id in client_ids:
                cache.delete(PER_APPOINTMENTS.format(client_id))
    # 返回成功响应
    return Response(serializer.data, status=status.HTTP_200_OK)


# 管理员或员工查询所有排班
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@permission_classes([IsAdmin | IsStaff])
def get_staff_schedule(request):
    schedules_data = cache.get(SCHEDULES_DATA)
    if not schedules_data:
        schedules = StaffSchedules.objects.all()
        serializer = StaffScheduleSerializer(schedules, many=True)
        schedules_data = serializer.data
        cache.set(SCHEDULES_DATA, schedules_data)
    return Response(schedules_data, status=status.HTTP_200_OK)


# 管理员或员工查询某员工今天包含今天之后所有的排班
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
def get_staff_schedule_after_today(request, staff_id):
    permission_classes = [IsAdmin | IsStaff]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    beijing_tz = pytz.timezone("Asia/Shanghai")
    now_beijing = datetime.now(beijing_tz)
    today_date = now_beijing.date()

    # 根据staff_id和assigned_date筛选出今天及以后（包含今天）的排班记录
    schedules = StaffSchedules.objects.filter(staff_id=staff_id, assigned_date__gte=today_date)
    serializer = StaffScheduleSerializer(schedules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_schedules_by_date(request, date):
    # 权限验证
    permission_classes = [IsAdmin | IsStaff]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    try:
        # 将日期字符串转换为日期对象
        assigned_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return Response({'error': "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    # 查询指定日期的所有排班记录
    schedules = StaffSchedules.objects.filter(assigned_date=assigned_date)
    serializer = StaffScheduleSerializer(schedules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_staff_schedule_by_date(request, date, staff_id):
    # 权限验证
    permission_classes = [IsAdmin | IsStaff]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    try:
        # 将日期字符串转换为日期对象
        assigned_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return Response({'error': "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 查询指定日期和员工ID的排班记录
        schedules = StaffSchedules.objects.filter(staff_id=staff_id, assigned_date=assigned_date)
        serializer = StaffScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except StaffSchedules.DoesNotExist:
        return Response({'error': "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)


# 管理员或员工查询某员工所有的排班
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@permission_classes([IsAdmin | IsStaff])
def get_staff_schedule_certain(request, staff_id):
    schedules_data = cache.get(PER_SCHEDULES.format(staff_id))
    if not schedules_data:
        schedules = StaffSchedules.objects.filter(staff_id=staff_id)
        serializer = StaffScheduleSerializer(schedules, many=True)
        schedules_data = serializer.data
        cache.set(PER_SCHEDULES.format(staff_id), schedules_data)
    return Response(schedules_data, status=status.HTTP_200_OK)


# 管理员删除排班
@swagger_auto_schema(
    method="DELETE",
)
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_staff_schedule(request, pk):
    schedule = StaffSchedules.objects.get(pk=pk)
    staff_id = schedule.staff_id
    schedule.delete()
    cache.delete(SCHEDULES_DATA)
    cache.delete(PER_SCHEDULES.format(staff_id))
    return Response({'msg': 'delete success'}, status=status.HTTP_200_OK)


# 查询食材
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@login_required
def get_ingredient(request):
    cache_key = INGREDIENTS_DATA
    ingredients_data = cache.get(cache_key)
    if not ingredients_data:
        ingredients = Ingredients.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        ingredients_data = serializer.data  # 缓存序列化后的数据
        cache.set(cache_key, ingredients_data)
    return Response(ingredients_data, status=status.HTTP_200_OK)


# 管理员或员工新增食材
@swagger_auto_schema(
    method="POST",
    request_body=IngredientSerializer,
)
@api_view(["POST"])
@permission_classes([IsAdmin | IsStaff])
def create_ingredient(request):
    serializer = IngredientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        cache.delete(INGREDIENTS_DATA)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员或员工更新食材
@swagger_auto_schema(
    method="PATCH",
    request_body=IngredientSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdmin | IsStaff])
def update_ingredient(request):
    ingredient = Ingredients.objects.get(pk=request.data["ingredient_id"])
    serializer = IngredientSerializer(ingredient, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        cache.delete(INGREDIENTS_DATA)
        if RecipeIngredient.objects.filter(ingredient_id=ingredient).exists():
            cache.delete(RECIPES_DATA)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员或员工删除食材
@swagger_auto_schema(
    method="DELETE",
)
@api_view(["DELETE"])
@permission_classes([IsAdmin | IsStaff])
def delete_ingredient(request, pk):
    is_used_in_recipes = RecipeIngredient.objects.filter(ingredient_id=pk).exists()
    Ingredients.objects.filter(pk=pk).delete()
    cache.delete(INGREDIENTS_DATA)
    if is_used_in_recipes:
        cache.delete(RECIPES_DATA)
    return Response({'msg': 'delete success'}, status=status.HTTP_200_OK)


# 获取所有菜谱
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@login_required
def get_recipe(request):
    recipes_data = cache.get(RECIPES_DATA)
    if not recipes_data:
        recipes = FoodRecipes.objects.all()
        serializer = FoodRecipeSerializer(recipes, many=True)
        recipes_data = serializer.data
        cache.set(RECIPES_DATA, recipes_data)
    return Response(recipes_data, status=status.HTTP_200_OK)


# 管理员或员工新增菜谱
@swagger_auto_schema(
    method="POST",
    request_body=CreateRecipeSerializer,
)
@api_view(["POST"])
@permission_classes([IsAdmin | IsStaff])
def create_recipe(request):
    serializer = CreateRecipeSerializer(data=request.data)
    if serializer.is_valid():
        recipe = serializer.save()
        cache.delete(RECIPES_DATA)
        return Response(FoodRecipeSerializer(recipe).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员或员工修改菜谱
@swagger_auto_schema(
    method="PATCH",
    request_body=UpdateRecipeSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdmin | IsStaff])
def update_recipe(request):
    serializer = UpdateRecipeSerializer(data=request.data)
    if serializer.is_valid():
        recipe_id = serializer.validated_data['recipe_id']
        try:
            recipe = FoodRecipes.objects.get(recipe_id=recipe_id)
        except FoodRecipes.DoesNotExist:
            return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

        updated_recipe = serializer.update(recipe, serializer.validated_data)
        cache.delete(RECIPES_DATA)
        return Response(FoodRecipeSerializer(updated_recipe).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 管理员或员工删除菜谱
@swagger_auto_schema(
    method="DELETE",
)
@api_view(["DELETE"])
@permission_classes([IsAdmin | IsStaff])
def delete_recipe(request, pk):
    try:
        recipe = FoodRecipes.objects.get(recipe_id=pk)
        recipe.delete()  # 删除菜谱会级联删除 RecipeIngredient 记录
        cache.delete(RECIPES_DATA)
        return Response(status=status.HTTP_200_OK)
    except FoodRecipes.DoesNotExist:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)


# 根据忌口条件筛选不包含忌口菜谱
# 请求示例 GET /get_recipe_by_avoidance/?avoidance=鸡蛋,大蒜
@swagger_auto_schema(
    method="GET",
    manual_parameters=[avoidance_param]
)
@api_view(["GET"])
def get_recipe_by_avoidance(request):
    avoidance = request.GET.get('avoidance', '').split(',')
    if avoidance and avoidance[0]:  # 检查是否有有效的忌口参数
        # 找到包含忌口食材的菜谱 ID
        recipes_with_avoidance = RecipeIngredient.objects.filter(
            ingredient__ingredient_name__in=avoidance
        ).values_list('recipe_id', flat=True).distinct()
        # 排除这些菜谱
        recipes = FoodRecipes.objects.exclude(recipe_id__in=recipes_with_avoidance)
    else:
        recipes = FoodRecipes.objects.all()

    serializer = FoodRecipeSerializer(recipes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 根据爱吃条件筛选包含爱吃食物的菜谱
@swagger_auto_schema(
    method="GET",
    manual_parameters=[preference_param]
)
@api_view(["GET"])
def get_recipe_by_preference(request):
    preference = request.GET.get('preference', '').split(',')
    if preference and preference[0]:  # 检查是否有有效的偏好参数
        # 找到包含爱吃食材的菜谱 ID
        recipes_with_preference = RecipeIngredient.objects.filter(
            ingredient__ingredient_name__in=preference
        ).values_list('recipe_id', flat=True).distinct()
        # 筛选这些菜谱
        recipes = FoodRecipes.objects.filter(recipe_id__in=recipes_with_preference)
    else:
        recipes = FoodRecipes.objects.all()

    serializer = FoodRecipeSerializer(recipes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 查询某客户所有的膳食计划
@swagger_auto_schema(
    method="GET",
)
@api_view(["GET"])
@permission_classes([IsAdmin | IsStaff | IsClient])
def get_diet_plan(request, client_id):
    diet_plans_data = cache.get(DIET_PLANS.format(client_id))
    if not diet_plans_data:
        try:
            # 查询指定客户的所有膳食计划
            diet_plans = DietPlans.objects.filter(client_id=client_id)
            serializer = DietPlanSerializer(diet_plans, many=True)
            diet_plans_data = serializer.data
            cache.set(DIET_PLANS.format(client_id), diet_plans_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(diet_plans_data, status=status.HTTP_200_OK)


# 请求示例：GET /diet_plans/certain_day/?client_id=1&diet_date=2023-03-02
# 查询某客户【client_id】某日【diet_date】膳食计划
@swagger_auto_schema(
    method="GET",
    manual_parameters=[client_id_param, diet_date_param]
)
@api_view(["GET"])
@permission_classes([IsAdmin | IsStaff | IsClient])
def get_certain_day_diet_plan(request):
    client_id = request.GET.get('client_id')
    diet_date = request.GET.get('diet_date')

    # 验证参数
    if not client_id or not diet_date:
        return Response({'error': 'client_id and diet_date are required'}, status=status.HTTP_400_BAD_REQUEST)

    diet_plan_data = cache.get(PER_DIET_PLAN.format(client_id=client_id, diet_date=diet_date))
    if not diet_plan_data:
        try:
            # 查询指定客户某日的膳食计划
            diet_plan = DietPlans.objects.get(client_id=client_id, diet_date=diet_date)
            serializer = CertainDayDietPlanSerializer(diet_plan)
            diet_plan_data = serializer.data
            cache.set(PER_DIET_PLAN.format(client_id=client_id, diet_date=diet_date), diet_plan_data)
        except DietPlans.DoesNotExist:
            return Response({'error': 'Diet plan not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(diet_plan_data, status=status.HTTP_200_OK)


# 员工或管理员新建某客户【client_id】某日【diet_date】某餐【type】膳食计划，和新建逻辑类似
@swagger_auto_schema(
    method="PATCH",
    request_body=UpdateDietPlanSerializer,
)
@api_view(["PATCH"])
@permission_classes([IsAdmin | IsStaff])
def update_diet_plan(request):
    serializer = UpdateDietPlanSerializer(data=request.data)
    if serializer.is_valid():
        diet_plan_id = serializer.validated_data['diet_plan_id']
        try:
            diet_plan = DietPlans.objects.get(diet_plan_id=diet_plan_id)
            updated_diet_plan = serializer.update(diet_plan, serializer.validated_data)
            return Response(DietPlanSerializer(updated_diet_plan).data, status=status.HTTP_200_OK)
        except DietPlans.DoesNotExist:
            return Response({'error': 'Diet plan not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 员工或管理员删除某【diet_plan_id】某餐【type】膳食计划
@swagger_auto_schema(
    method="DELETE",
    request_body=DeleteDietPlanSerializer,
)
@api_view(["DELETE"])
def delete_diet_plan(request):
    permission_classes = [IsAdmin | IsStaff]
    for permission in permission_classes:
        if not permission().has_permission(request, None):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    diet_plan_id = request.data.get('diet_plan_id')
    meal_type = request.data.get('type')

    if not diet_plan_id or not meal_type:
        return Response({'error': 'diet_plan_id and type are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        diet_plan = DietPlans.objects.get(diet_plan_id=diet_plan_id)
        # 删除指定餐次的记录
        PlanRecipe.objects.filter(diet_plan=diet_plan, type=meal_type).delete()

        # 重新计算总营养摄入
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

        diet_plan.nutrition_taken = total
        diet_plan.save()
        return Response(status=status.HTTP_200_OK)
    except DietPlans.DoesNotExist:
        return Response({'error': 'Diet plan not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method="DELETE")
@api_view(["DELETE"])
@permission_classes([IsAdmin | IsStaff])
def delete_entire_diet_plan(request, diet_plan_id):
    try:
        # 获取并删除膳食计划
        diet_plan = DietPlans.objects.get(diet_plan_id=diet_plan_id)
        client_id = diet_plan.client_id
        diet_plan.delete()
        cache.delete(DIET_PLANS.format(client_id))
        return Response(status=status.HTTP_200_OK)
    except DietPlans.DoesNotExist:
        return Response({'error': 'Diet plan not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method="PATCH", request_body=UpdateDietPlanFieldsSerializer)
@api_view(["PATCH"])
@permission_classes([IsAdmin | IsStaff])
def update_diet_plan_fields(request, diet_plan_id):
    try:
        # 获取膳食计划
        diet_plan = DietPlans.objects.get(diet_plan_id=diet_plan_id)
        client_id = diet_plan.client_id
        diet_date = request.data['diet_date']
    except DietPlans.DoesNotExist:
        return Response({'error': 'Diet plan not found'}, status=status.HTTP_404_NOT_FOUND)

    # 更新部分字段
    serializer = UpdateDietPlanFieldsSerializer(diet_plan, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        cache.delete(DIET_PLANS.format(client_id))
        cache.delete(PER_DIET_PLAN.format(client_id=client_id, diet_date=diet_date))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="POST", request_body=CreateDietPlanRecordSerializer)
@api_view(["POST"])
@permission_classes([IsAdmin | IsStaff])
def create_diet_plan_record(request):
    # 创建新记录
    serializer = CreateDietPlanRecordSerializer(data=request.data)
    if serializer.is_valid():
        diet_plan = serializer.save()
        cache.delete(DIET_PLANS.format(request.data['client']))
        return Response(CreateDietPlanRecordSerializer(diet_plan).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="获取在指定日期和时间段内有班次且无预约的员工列表",
    manual_parameters=[
        openapi.Parameter(
            'date',
            openapi.IN_QUERY,
            description="日期，格式为 YYYY-MM-DD",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'start_time',
            openapi.IN_QUERY,
            description="开始时间，格式为 HH:MM:SS",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'end_time',
            openapi.IN_QUERY,
            description="结束时间，格式为 HH:MM:SS",
            type=openapi.TYPE_STRING,
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            description="员工列表",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'staff_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        )
    }
)
@api_view(['GET'])
@login_required
def available_staff(request):
    # 获取查询参数
    date_str = request.GET.get('date')
    start_time_str = request.GET.get('start_time')
    end_time_str = request.GET.get('end_time')

    # 检查参数是否完整
    if not all([date_str, start_time_str, end_time_str]):
        return Response({'error': 'Missing parameters'}, status=400)

    # 解析日期和时间
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
    except ValueError:
        return Response({'error': 'Invalid date or time format'}, status=400)

    # 查询可用员工
    free_staff = Staff.objects.filter(
        staffschedules__assigned_date=date,
        staffschedules__template__start_time__lte=start_time,
        staffschedules__template__end_time__gte=end_time
    ).annotate(
        overlapping=Count('appointments', filter=Q(
            appointments__schedule_date=date,
            appointments__schedule_time__lt=end_time,
            appointments__end_time__gt=start_time,
            appointments__state__in=["待确认", "已预约"]
        ))
    ).filter(overlapping=0).distinct()
    # 序列化并返回结果
    serializer = AvailableStaffSerializer(free_staff, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="GET",
)
@api_view(['GET'])
@login_required
def get_notifications(request):
    """获取当前用户的通知"""
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="PATCH",
)
@api_view(['PATCH'])
@login_required
def mark_notification_read(request, pk):
    """标记指定通知为已读"""
    try:
        notification = Notification.objects.get(id=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='PATCH',
)
@api_view(['PATCH'])
@permission_classes([IsAdmin | IsStaff])
def generate_diet_recommendation(request, diet_plan_id):
    try:
        diet_plan = DietPlans.objects.get(pk=diet_plan_id)
    except DietPlans.DoesNotExist:
        return Response({'error': 'diet plan does not exist'}, status=status.HTTP_404_NOT_FOUND)

    client = diet_plan.client
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz).date()
    past_dates = [today - timedelta(days=i) for i in range(1, 4)]
    past_diet_plans = DietPlans.objects.filter(client=client, diet_date__in=past_dates).order_by('diet_date')

    diet_record_str = "过去三天的膳食记录：\n"
    for past_plan in past_diet_plans:
        recipes = PlanRecipe.objects.filter(diet_plan=past_plan)
        day_str = f"{past_plan.diet_date}: "
        for pr in recipes:
            day_str += f"{pr.type} - {pr.recipe.recipe_name}, "
        diet_record_str += day_str.rstrip(', ') + "\n"
    if not past_diet_plans:
        diet_record_str = "无过去三天的膳食记录。"

    # 获取用户的饮食偏好
    dietary_preference = client.dietary_preference or {}
    taboo_ingredients = dietary_preference.get('忌口', [])
    favorite_ingredients = dietary_preference.get('爱吃', [])
    taboo_ingredients_str = ", ".join(taboo_ingredients) if taboo_ingredients else "无"
    favorite_ingredients_str = ", ".join(favorite_ingredients) if favorite_ingredients else "无"

    # 获取所有食谱作为 recipe_book
    recipe_book_str = "菜谱：\n"
    for recipe in FoodRecipes.objects.all():
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        ingredient_names = ", ".join([ri.ingredient.ingredient_name for ri in ingredients])
        nutrition = ", ".join(
            [f"{k}: {v}%" for k, v in (recipe.nutrition_info or {}).items()]) if recipe.nutrition_info else "无"
        recipe_book_str += f"{recipe.recipe_name}: 食材 - {ingredient_names}; 营养 - {nutrition}\n"

    # 获取营养需求
    nutrition_requirements = diet_plan.nutrition_requirements or {}
    nutrition_req_str = ", ".join(
        [f"{k}: {v}%" for k, v in nutrition_requirements.items()]) if nutrition_requirements else "无"

    # 获取用户信息
    gender = client.gender
    birth_date = client.birth_date
    age = (today - birth_date).days // 365 if birth_date else None
    medical_history = client.medical_history or "无"

    # 调用大模型接口获取推荐
    recommendation = get_diet_recommend(
        diet_record=diet_record_str,
        taboo_ingredients=taboo_ingredients_str,
        favorite_ingredients=favorite_ingredients_str,
        recipe_book=recipe_book_str,
        nutrition_requirements=nutrition_req_str,
        gender=gender,
        age=age,
        medical_history=medical_history
    )

    # 保存推荐结果到 smart_recommendation 字段
    diet_plan.smart_recommendation = recommendation
    diet_plan.save()
    client_id = diet_plan.client_id
    diet_date = diet_plan.diet_date
    cache.delete(DIET_PLANS.format(client_id))
    cache.delete(PER_DIET_PLAN.format(client_id=client_id, diet_date=diet_date))
    return Response({'smart_recommendation': recommendation}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="PATCH",
)
@api_view(["PATCH"])
@permission_classes([IsAdmin | IsStaff])
def generate_metrics_assessment(request, metric_id):
    try:
        metric = HealthMetrics.objects.get(pk=metric_id)
    except HealthMetrics.DoesNotExist:
        return Response({'error': 'metric does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # 获取用户信息  
    client = metric.client
    age = calculate_age(client.birth_date)
    sex = client.gender
    marital = client.marital
    income_category = client.income_range
    race = 'Asian'
    vital_signs = metric.vital_signs
    mets_probability = metric.mets_probability
    
    assessment = get_metrics_assessment(age, sex, marital, income_category, race, vital_signs, mets_probability)

    metric.smart_assessment = assessment
    metric.save()
    cache.delete(PER_METRICS.format(client.client_id))
    return Response({'smart_assessment': assessment}, status=status.HTTP_200_OK)

