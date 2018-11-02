# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField
from datatemplate.models import *
from django.contrib.admin import widgets
from django.contrib.auth.models import User
class AddForm (forms.Form):
    a = forms.CharField(widget=forms.Textarea(attrs={'cols': 200, 'rows': 10}))
class DataTemplateMgr(forms.Form):
    a = forms.CharField(widget=forms.Textarea(attrs={'cols': 200, 'rows': 10}))
    begin = forms.DateTimeField(label='dateinfo')
