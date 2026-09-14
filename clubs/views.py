from django.http import JsonResponse

from .models import Club


def club_list(request):
    if request.method != 'GET':
        return JsonResponse({'detail': '只支持 GET 请求'}, status=405)

    clubs = []
    for club in Club.objects.prefetch_related('administrators__user').all():
        clubs.append({
            'id': club.id,
            'name': club.name,
            'description': club.description,
            'category': club.category,
            'founded_date': club.founded_date.isoformat(),
            'location': club.location,
            'administrators': [
                {
                    'id': admin.id,
                    'real_name': admin.real_name,
                    'username': admin.user.username,
                    'is_staff': admin.user.is_staff,
                    'phone': admin.phone,
                    'email': admin.email,
                }
                for admin in club.administrators.all()
            ],
        })

    return JsonResponse({
        'count': len(clubs),
        'results': clubs,
    }, json_dumps_params={'ensure_ascii': False})
