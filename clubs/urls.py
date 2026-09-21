from django.urls import path

from . import views

urlpatterns = [
    path('', views.ClubListView.as_view(), name='club-index'),
    path('clubs/new/', views.ClubCreateView.as_view(), name='club-create'),
    path('clubs/<int:pk>/', views.ClubDetailView.as_view(), name='club-detail'),
    path('clubs/<int:pk>/edit/', views.ClubUpdateView.as_view(), name='club-update'),
    path('clubs/<int:pk>/delete/', views.ClubDeleteView.as_view(), name='club-delete'),
    path('api/clubs/', views.club_list, name='club-list'),
]
