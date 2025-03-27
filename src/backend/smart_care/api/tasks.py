from celery import shared_task
from django.utils import timezone
from .models import Appointments, CarePlans, Notification, Users, Roles
from datetime import timedelta, datetime
import pytz

@shared_task
def send_admin_notification():
    """每小时检查未指定员工的预约并通知管理员"""
    appointments = Appointments.objects.filter(staff__isnull=True, state__in=['待确认', '已预约'])
    if appointments.exists():
        admins = Users.objects.filter(role__role_name='管理员')
        message = f"有 {appointments.count()} 个预约未指定员工，请尽快处理。"
        for admin in admins:
            Notification.objects.create(user=admin, message=message)

@shared_task
def send_appointment_reminders():
    """检查即将到来的预约并发送提醒"""
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    reminders = [
        timedelta(hours=24),
        timedelta(hours=1),
        timedelta(minutes=30),
    ]
    for reminder in reminders:
        remind_time = now + reminder
        appointments = Appointments.objects.filter(
            schedule_date=remind_time.date(),
            schedule_time__gte=(remind_time - timedelta(minutes=1)).time(),
            schedule_time__lte=(remind_time + timedelta(minutes=1)).time(),
            state__in=['待确认', '已预约']
        )
        for appointment in appointments:
            message = f"您有一个预约即将开始，服务：{appointment.service.service_name}，时间：{appointment.schedule_date} {appointment.schedule_time}。"
            if appointment.staff:
                Notification.objects.create(user=appointment.staff.user, message=message)
            Notification.objects.create(user=appointment.client.user, message=message)

@shared_task
def send_care_plan_reminders():
    """每天早上6点提醒未结束的护理计划"""
    care_plans = CarePlans.objects.filter(plan_state__in=['待开始', '进行中'])
    for plan in care_plans:
        if plan.staff:
            client_name = f"{plan.client.user.last_name} {plan.client.user.first_name}"
            message = f"您有未完成的护理计划，客户：{client_name}，开始时间：{plan.start_date}，结束时间：{plan.end_date}。"
            Notification.objects.create(user=plan.staff.user, message=message)

@shared_task
def clean_old_notifications():
    """删除7天前的已读通知"""
    threshold = timezone.now() - timedelta(days=7)
    Notification.objects.filter(is_read=True, created_at__lt=threshold).delete()