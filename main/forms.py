from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Review, UserProfile

class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱地址'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请确认密码'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )

class ReviewForm(forms.ModelForm):
    """评论表单"""
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5', 'placeholder': '评分 1-5'})
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'placeholder': '请输入您的评论...'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'content']

class ProfileUpdateForm(forms.ModelForm):
    """个人资料更新表单"""
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': '请输入个人简介...'}),
        required=False
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )
    favorite_categories = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：动作,喜剧,科幻'}),
        required=False,
        help_text='请输入您喜欢的影视分类，用逗号分隔'
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'birth_date', 'favorite_categories']

class SearchForm(forms.Form):
    """搜索表单"""
    query = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '搜索电影、剧集、演员...'}),
        required=False
    )