from django import forms
from django.forms import ModelForm, Textarea
from . import models

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

import datetime

class ExpenseCreateForm(ModelForm):
	class Meta:
		model = models.Expense

		fields = ['title', 'amount', 'date', 'description']

		widgets = {
			'date': forms.DateInput(attrs = {'type': 'date', 'class': 'date_field', 'value': '2018-11-09'}),
			'description': forms.Textarea(attrs = {'cols': 40, 'rows': 3})
		}

class FilterForm(forms.Form):
	start_date = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date', 'class': 'date_field'}))
	end_date = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date', 'class': 'date_field'}))


class userBasicForm(forms.ModelForm):
	password = forms.CharField(widget = forms.PasswordInput())

	class Meta():
		model = User
		fields = ('username', 'email', 'password', 'first_name', 'last_name')

class UserRegistrationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'first_name', 'last_name',  'password1', 'password2']

	def clean_email(self):
		email = self.cleaned_data.get('email')
		username = self.cleaned_data.get('username')
		if email and User.objects.filter(email=email).count() > 0:
			raise forms.ValidationError('This email address is already registered.')
		return email
