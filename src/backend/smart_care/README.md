# SmartCare 智能养老系统

## 项目概述

SmartCare是一个全面的智能养老管理系统，旨在提供高效、智能化的养老服务管理解决方案。系统集成了客户管理、护理计划、预约服务、饮食规划、健康监测等核心功能，辅以智能推荐和数据分析能力，为养老机构提供全方位的管理工具。

## 技术架构

### 后端架构
- **Web框架**: Django 5.1.6
- **API接口**: Django REST Framework 3.15.2
- **数据库**: MySQL
- **缓存系统**: Redis
- **异步任务队列**: Celery 5.4.0
- **实时通知**: django-eventstream（未使用，后续采取的方案是前端轮询）
- **API文档**: drf-yasg (Swagger)

### 数据存储
- 关系型数据库(MySQL)用于存储结构化数据
- Redis用于缓存和消息队列
- JSONField用于存储半结构化数据(如营养信息、紧急联系人等)

### 系统集成
- 支持RESTful API接口
- CORS跨域资源共享
- 基于Token的认证系统

## 核心功能模块

### 用户管理
- 多角色支持(管理员、员工、客户)
- 完整的用户注册、登录、密码重置流程
- 基于权限的访问控制

### 客户管理
- 客户信息档案管理
- 健康历史记录
- 个人偏好设置(饮食偏好等)

### 护理计划管理
- 创建和管理个性化护理计划
- 护理目标设置与跟踪
- 计划执行进度报告
- 满意度评价系统

### 预约服务
- 服务预约管理
- 员工排班与调度
- 预约提醒系统
- 服务满意度评价

### 健康监测
- 生命体征记录
- 健康指标分析
- 智能健康评估报告

### 饮食管理
- 个性化饮食计划
- 食谱管理与推荐
- 营养摄入分析
- 食材配料管理

### 通知系统
- 实时消息推送
- 预约提醒
- 护理计划提醒
- 管理员通知

### 排班系统
- 员工班次模板管理
- 灵活排班安排
- 日程管理

## 智能特性

系统集成了智能推荐和评估功能:
- 智能饮食推荐
- 健康状况智能评估
- 基于客户需求的服务匹配

## 数据模型

系统包含多个关联的数据模型:
- Users (用户)
- Roles (角色)
- Clients (客户)
- Staff (员工)
- CarePlans (护理计划)
- PlanGoals (计划目标)
- Appointments (预约)
- Services (服务)
- HealthMetrics (健康指标)
- DietPlans (饮食计划)
- FoodRecipes (食谱)
- Ingredients (食材)
- StaffSchedules (员工排班)
- ShiftTemplates (班次模板)
- Notification (通知)

## 定时任务

系统配置了多个定时任务:
- 未分配员工的预约通知
- 即将到来的预约提醒
- 护理计划每日提醒
- 清理旧通知记录

## 开发与部署

### 开发环境
- Python 3.x
- Django 5.1.6
- MySQL数据库
- Redis服务
- Celery worker & beat

### 依赖管理
- 使用requirements.txt管理项目依赖

### API文档
- 使用Swagger提供交互式API文档
- 访问路径: /swagger/

## 安全特性

### 1. 认证与授权
- **基于角色的访问控制(RBAC)**
  - 使用Django的`permissions.BasePermission`实现自定义权限类
  - 实现了`IsAdmin`、`IsStaff`、`IsClient`三种权限类
  - 通过`@permission_classes`装饰器进行权限验证
  - 支持权限组合（如`IsAdmin | IsStaff`）

- **用户认证**
  - 使用Django的`AbstractUser`作为基础用户模型
  - 自定义`Users`模型继承`AbstractUser`并扩展角色关联
  - 使用`@login_required`装饰器保护需要登录的视图
  - 实现了完整的登录、注册、密码重置流程

### 2. 密码安全
- **密码加密存储**
  - 使用Django的`make_password`和`check_password`进行密码加密和验证
  - 密码字段使用`write_only=True`确保不返回给前端
  - 实现了安全的密码重置机制

### 3. 会话管理
- **会话配置**
  - 使用数据库存储会话（`django.contrib.sessions.backends.db`）
  - 设置会话过期时间为两周
  - 浏览器关闭时保持会话有效
  - 支持会话自动续期

### 4. CSRF保护
- **跨站请求伪造防护**
  - 启用Django的CSRF中间件
  - 配置`CSRF_TRUSTED_ORIGINS`允许特定源
  - 前端请求自动携带CSRF令牌

### 5. CORS安全
- **跨域资源共享控制**
  - 使用`django-cors-headers`中间件
  - 配置`CORS_ALLOW_CREDENTIALS`支持凭证
  - 限制允许的源（`CORS_ALLOWED_ORIGINS`）

### 6. 数据安全
- **输入验证**
  - 使用Django REST Framework的序列化器进行数据验证
  - 实现自定义验证逻辑
  - 防止SQL注入和XSS攻击

- **缓存安全**
  - 使用Redis进行缓存
  - 设置缓存超时时间
  - 敏感数据不缓存

### 7. 安全中间件
- **安全中间件配置**
  - `SecurityMiddleware`: 提供基本的安全功能
  - `SessionMiddleware`: 会话管理
  - `AuthenticationMiddleware`: 用户认证
  - `CsrfViewMiddleware`: CSRF保护
  - `XFrameOptionsMiddleware`: 防止点击劫持

### 8. 用户状态管理
- **账号状态控制**
  - 支持账号激活/禁用
  - 密码重置状态跟踪
  - 登录失败处理
  - 最后登录时间记录

### 9. API安全
- **API访问控制**
  - 使用Swagger进行API文档管理
  - 接口权限验证
  - 请求频率限制
  - 敏感操作日志记录

### 10. 安全配置
- **生产环境安全**
  - 敏感配置分离
  - 密钥管理
  - 调试模式控制
  - 错误信息处理
