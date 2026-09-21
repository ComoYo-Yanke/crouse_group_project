from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
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


def club_list(request):
    if request.method != 'GET':
        return JsonResponse({'detail': '只支持 GET 请求'}, status=405)

    clubs = [
        serialize_club(club)
        for club in Club.objects.prefetch_related('administrators__user').all()
    ]
    return JsonResponse({
        'count': len(clubs),
        'results': clubs,
    }, json_dumps_params={'ensure_ascii': False})


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
