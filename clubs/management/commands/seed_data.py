from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from clubs.models import Club, ClubAdministrator


SEED_CLUBS = [
    {
        'name': '篮球社',
        'description': '面向全校篮球爱好者，定期组织校内联赛与训练。',
        'category': '体育',
        'founded_date': date(2018, 9, 1),
        'location': '体育馆一楼',
    },
    {
        'name': '摄影社',
        'description': '学习摄影构图与后期，记录校园活动与风景。',
        'category': '艺术',
        'founded_date': date(2019, 3, 15),
        'location': '艺术楼 203',
    },
    {
        'name': '音乐社',
        'description': '声乐、器乐排练与演出，举办校园音乐会。',
        'category': '艺术',
        'founded_date': date(2017, 10, 8),
        'location': '学生活动中心排练厅',
    },
    {
        'name': '志愿者社',
        'description': '组织校园与社区志愿服务，开展公益实践。',
        'category': '公益',
        'founded_date': date(2016, 5, 20),
        'location': '社团办公室 101',
    },
]

SEED_ADMINS = [
    {
        'username': '社团管理员1',
        'real_name': '社团管理员1',
        'phone': '13800001111',
        'email': 'clubadmin1@example.com',
        'club_name': '篮球社',
    },
    {
        'username': '社团管理员2',
        'real_name': '社团管理员2',
        'phone': '13800002222',
        'email': 'clubadmin2@example.com',
        'club_name': '摄影社',
    },
    {
        'username': '社团管理员3',
        'real_name': '社团管理员3',
        'phone': '13800003333',
        'email': 'clubadmin3@example.com',
        'club_name': '音乐社',
    },
    {
        'username': '社团管理员4',
        'real_name': '社团管理员4',
        'phone': '13800004444',
        'email': 'clubadmin4@example.com',
        'club_name': '志愿者社',
    },
]

DEFAULT_PASSWORD = 'Admin123456'


class Command(BaseCommand):
    help = '写入社团测试数据，并创建 4 个后台社团管理员账号'

    def handle(self, *args, **options):
        clubs = {}
        for item in SEED_CLUBS:
            club, created = Club.objects.update_or_create(
                name=item['name'],
                defaults=item,
            )
            clubs[club.name] = club
            self.stdout.write(self.style.SUCCESS(
                f"{'创建' if created else '更新'}社团: {club.name}"
            ))

        for item in SEED_ADMINS:
            user, created = User.objects.get_or_create(
                username=item['username'],
                defaults={
                    'email': item['email'],
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                    'first_name': item['real_name'],
                },
            )
            if created:
                user.set_password(DEFAULT_PASSWORD)
            user.email = item['email']
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.first_name = item['real_name']
            user.save()

            ClubAdministrator.objects.update_or_create(
                user=user,
                defaults={
                    'club': clubs[item['club_name']],
                    'real_name': item['real_name'],
                    'phone': item['phone'],
                    'email': item['email'],
                },
            )
            self.stdout.write(self.style.SUCCESS(
                f"{'创建' if created else '更新'}后台用户: {user.username}"
            ))

        self.stdout.write(self.style.WARNING(
            f'后台登录地址 /admin/ ，默认密码: {DEFAULT_PASSWORD}'
        ))
