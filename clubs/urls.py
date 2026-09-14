from django.urls import path

from . import views

urlpatterns = [
    path('clubs/', views.club_list, name='club-list'),
]
