import json

from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ClubForm
from .models import Club


def serialize_club(club):
    return {
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
    }


def json_response(data, status=200):
    # ensure_ascii=False 让中文原样输出，小程序里不用再解转义
    return JsonResponse(data, status=status, json_dumps_params={'ensure_ascii': False})


def parse_body(request):
    """解析 JSON 请求体，格式不对返回 None。"""
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except (ValueError, UnicodeDecodeError):
        return None


def form_errors(form):
    """把 Django 表单错误整理成 {字段: [错误信息]}，方便小程序展示。"""
    return {field: [str(e) for e in errs] for field, errs in form.errors.items()}


@csrf_exempt
def club_list(request):
    if request.method == 'GET':
        clubs = [
            serialize_club(club)
            for club in Club.objects.prefetch_related('administrators__user').order_by('id')
        ]
        return json_response({'count': len(clubs), 'results': clubs})

    if request.method == 'POST':
        data = parse_body(request)
        if data is None:
            return json_response({'detail': '请求体不是合法的 JSON'}, status=400)

        form = ClubForm(data)
        if not form.is_valid():
            return json_response(
                {'detail': '表单校验失败', 'errors': form_errors(form)}, status=400
            )
        return json_response(serialize_club(form.save()), status=201)

    return json_response({'detail': '只支持 GET / POST 请求'}, status=405)


@csrf_exempt
def club_detail_api(request, pk):
    club = Club.objects.filter(pk=pk).first()
    if club is None:
        return json_response({'detail': '社团不存在'}, status=404)

    if request.method == 'GET':
        return json_response(serialize_club(club))

    if request.method in ('PUT', 'PATCH'):
        data = parse_body(request)
        if data is None:
            return json_response({'detail': '请求体不是合法的 JSON'}, status=400)

        form = ClubForm(data, instance=club)
        if not form.is_valid():
            return json_response(
                {'detail': '表单校验失败', 'errors': form_errors(form)}, status=400
            )
        return json_response(serialize_club(form.save()))

    if request.method == 'DELETE':
        name = club.name
        club.delete()
        return json_response({'detail': f'已删除社团「{name}」'})

    return json_response({'detail': '只支持 GET / PUT / DELETE 请求'}, status=405)


class ClubListView(ListView):
    model = Club
    template_name = 'clubs/club_list.html'
    context_object_name = 'clubs'
    queryset = Club.objects.prefetch_related('administrators').order_by('id')


class ClubDetailView(DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'
    context_object_name = 'club'
    queryset = Club.objects.prefetch_related('administrators__user')


class ClubCreateView(CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/club_form.html'
    success_url = reverse_lazy('club-index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '新增社团'
        context['submit_text'] = '创建社团'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'已创建社团「{form.instance.name}」。')
        return super().form_valid(form)


class ClubUpdateView(UpdateView):
    model = Club
    form_class = ClubForm
    template_name = 'clubs/club_form.html'

    def get_success_url(self):
        return reverse_lazy('club-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'编辑社团：{self.object.name}'
        context['submit_text'] = '保存修改'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'已更新社团「{form.instance.name}」。')
        return super().form_valid(form)


class ClubDeleteView(DeleteView):
    model = Club
    template_name = 'clubs/club_confirm_delete.html'
    context_object_name = 'club'
    success_url = reverse_lazy('club-index')

    def form_valid(self, form):
        messages.success(self.request, f'已删除社团「{self.object.name}」。')
        return super().form_valid(form)
