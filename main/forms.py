from django import forms
from django.forms import ModelForm
from . import models

from django.contrib.auth.models import User

import datetime

class ExpenseCreateForm(ModelForm):
	class Meta:
		model = models.Expense
		# fields = ['title', 'amount', 'date']
		fields = ['title', 'amount', 'date']
		widgets = {
			'date': forms.DateInput(attrs = {'type': 'date', 'class': 'date_field'})
		}

class FilterForm(forms.Form):
	start_date = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date', 'class': 'date_field'}))
	end_date = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date', 'class': 'date_field'}))


class userBasicForm(forms.ModelForm):
	password = forms.CharField(widget = forms.PasswordInput())

	class Meta():
		model = User
		fields = ('username', 'email', 'password', 'first_name', 'last_name')