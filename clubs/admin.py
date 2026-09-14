from django.contrib import admin

from .models import Club, ClubAdministrator


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'founded_date', 'location')
    search_fields = ('name', 'category')


@admin.register(ClubAdministrator)
class ClubAdministratorAdmin(admin.ModelAdmin):
    list_display = ('id', 'real_name', 'club', 'phone', 'email', 'user')
    search_fields = ('real_name', 'phone', 'email')
