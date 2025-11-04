"""
用户注册和密码重置相关视图
"""

from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User

class RegisterView(CreateView):
    """用户注册视图"""
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        """注册成功后的处理"""
        response = super().form_valid(form)
        messages.success(self.request, '注册成功！请登录您的账户')
        return response
    
    def form_invalid(self, form):
        """注册失败的处理"""
        messages.error(self.request, '注册失败，请检查您的输入')
        return super().form_invalid(form)

class CustomPasswordResetView(PasswordResetView):
    """自定义密码重置视图"""
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """密码重置邮件发送成功"""
        messages.success(self.request, '密码重置邮件已发送，请查收')
        return super().form_valid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """密码重置邮件发送完成视图"""
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """密码重置确认视图"""
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        """密码重置成功"""
        messages.success(self.request, '密码重置成功！您现在可以登录了')
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """密码重置完成视图"""
    template_name = 'password_reset_complete.html'