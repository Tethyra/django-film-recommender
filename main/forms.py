from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Review, UserProfile

class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}))

class ReviewForm(forms.ModelForm):
    """评论表单"""
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '请输入您的评论...'}),
        }
        labels = {
            'rating': '评分',
            'content': '评论内容',
        }

class ProfileUpdateForm(forms.ModelForm):
    """个人资料更新表单"""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'birth_date', 'favorite_categories']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'favorite_categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'avatar': '头像',
            'bio': '个人简介',
            'birth_date': '出生日期',
            'favorite_categories': '喜欢的分类',
        }

class SearchForm(forms.Form):
    """搜索表单"""
    query = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '搜索电影、剧集、演员...',
        'type': 'search'
    }))