from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    """Izoh qo'shish formasi"""
    class Meta:
        model = Comment
        fields = ('body',)  # author ni olib tashladik
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Izohingizni yozing...'
            }),
        }
        labels = {
            'body': 'Izoh',
        }


class ContactForm(forms.Form):
    """Bog'lanish formasi"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ismingiz'
        }),
        label="Ism"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email manzilingiz'
        }),
        label="Email"
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mavzu'
        }),
        label="Mavzu"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Xabaringizni yozing...'
        }),
        label="Xabar"
    )