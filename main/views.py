from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import DetailView, ListView
from . import models
from django.urls import reverse_lazy


from django import forms
from django.forms import ModelForm

import datetime

def Index(request):
	return render(request, "main/index.html")

class DateInput(forms.DateInput):
	input_type = 'date'

class ExpenseCreateForm(ModelForm):
	class Meta:
		model = models.Expense
		fields = ['title', 'amount', 'date']
		widgets = {
			'date': DateInput()
		}

class FilterFrom(forms.Form):
	start_date = forms.DateField(widget = DateInput())
	end_date = forms.DateField(widget = DateInput())

class ExpenseCreateView(CreateView):
	model = models.Expense
	form_class = ExpenseCreateForm

class ExpenseDetailView(DetailView):
	model = models.Expense

class ExpenseListView(ListView):
	model = models.Expense

class ExpenseDeleteView(DeleteView):
	model = models.Expense
	success_url = reverse_lazy('main:expense_list')

def filter_by_date(request):

	if request.method == "POST":
		formData = FilterFrom(request.POST)
		print(formData)
		if formData.is_valid():
			start_date = formData.cleaned_data['start_date']
			end_date = formData.cleaned_data['end_date']


		x = models.Expense.objects.filter(date__gte=start_date, date__lte=end_date)

		total = 0
		for e in x:
			total = total + e.amount

		return render(request, "main/filter_by_date.html", context = {'expenses': x, 'start_date': start_date, 'end_date': end_date, 'total': total})

	else:
		form = FilterFrom()
		return render(request, 'main/filterForm.html', context={'form': form})