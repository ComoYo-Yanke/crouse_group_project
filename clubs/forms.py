from django import forms

from .models import Club


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'category', 'founded_date', 'location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '例如：篮球社'}),
            'category': forms.TextInput(attrs={'placeholder': '例如：体育、艺术、公益'}),
            'founded_date': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.TextInput(attrs={'placeholder': '例如：体育馆一楼'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': '介绍社团宗旨、活动与招新信息'}),
        }
