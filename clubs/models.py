from django.contrib.auth.models import User
from django.db import models


class Club(models.Model):
    name = models.CharField('社团名称', max_length=100)
    description = models.TextField('社团信息')
    category = models.CharField('社团类型', max_length=50)
    founded_date = models.DateField('成立日期')
    location = models.CharField('活动地点', max_length=100, blank=True)

    class Meta:
        verbose_name = '社团'
        verbose_name_plural = '社团'

    def __str__(self):
        return self.name


class ClubAdministrator(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='后台账号',
        related_name='club_admin_profile',
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='administrators',
        verbose_name='所属社团',
    )
    real_name = models.CharField('管理员姓名', max_length=50)
    phone = models.CharField('联系电话', max_length=20)
    email = models.EmailField('邮箱')

    class Meta:
        verbose_name = '社团管理员'
        verbose_name_plural = '社团管理员'

    def __str__(self):
        return self.real_name
