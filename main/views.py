from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import DetailView, ListView, UpdateView
from . import models
from django import forms as djangoForms
from django.urls import reverse_lazy

from main.forms import FilterForm, ExpenseCreateForm

from datetime import datetime

from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin

from main import forms

from django.core.mail import send_mail

import random

from django.contrib.auth.models import User

import json

def make_dictionary(request):

	dictionary = {}

	if request.user.is_authenticated:
	
		user = request.user
		x = models.UserEmailConfirmation.objects.get(user = user)

		confirmed = x.confirmed
		dictionary.update({'confirmed': confirmed})

	return dictionary

def get_expenses_in_json(expenses):
	# print(expenses)

	prev_date = 0;

	grouped_expenses = {}
	list_of_dates = []

	for e in expenses:
		prev_date_str = str(prev_date)
		current_date = e.date


		if(str(current_date) in grouped_expenses):
			# print(str(current_date) + " exists in grouped_expenses.")
			pass
		else:
			# Updating dictionary with key as date_name and value as a dictionary an empty-array with its key as expenses.
			grouped_expenses.update(	
										{
											str(current_date): 
												{ 
													'expenses': [] 
												}  
										}
									)

		if(prev_date_str != str(current_date)):
			# print(current_date)
			prev_date = current_date
			list_of_dates.append(str(current_date))

		# Creating dictionary of current expense.
		current_expense_dictionary = { 'title': e.title, 'amount': e.amount}

		# print(current_expense_dictionary)

		# Updating the date dictionary with current expense dictionary.
		grouped_expenses[str(current_date)]['expenses'].append( current_expense_dictionary )
		# print("\n" + str(current_date) + ": " + str(grouped_expenses[str(current_date)]))



	# print("\n")
	# print(grouped_expenses)

	# for date in grouped_expenses:
		# print("\n" + date + ": ")

		# print("Total: " + str(len(grouped_expenses[date]['expenses'])))

		# print("{")
		# for x in range(1, len(grouped_expenses[date]['expenses']) ):
		# 	print("\t" + str(grouped_expenses[date]['expenses'][x]['title']) + " - " + str(grouped_expenses[date]['expenses'][x]['amount']) )
		# print("}")



	sum_dict = {}
	grand_total = 0
	for d in grouped_expenses:
		# Indexing date wise
		# print(d)

		sum_e = 0
		current_expense_list = grouped_expenses[d]['expenses']
		for e in current_expense_list:
			# Indexing expenses wise
			sum_e = sum_e + e['amount']
			grand_total = grand_total + e['amount']

		# print("Sum = " + str(sum_e))
		current_sum_dict = { str(d) : sum_e}

		sum_dict.update(current_sum_dict)

	sum_dict_json = json.dumps(sum_dict, sort_keys=True, indent=4)

	# print(sum_dict_json)

	grouped_expenses.update(
								{
									'date_wise_total': sum_dict,
									'grand_total': grand_total
								}
							)
	
	grouped_expenses_json = json.dumps(grouped_expenses, sort_keys=True, indent=4)
	
	# print(grouped_expenses_json)
	
	return grouped_expenses

def Index(request):
	dictionary = make_dictionary(request)

	return render(request, "main/index.html", context = dictionary)

def user_login(request):

	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('index'))
	else:
		if request.method == "GET":
			return render(request, "main/user_login.html")

		elif request.method == "POST":

			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(username = username, password = password)

			user_info = {}

			if user:
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect(reverse('index'))
				else:
					return HttpResponse("<h1>Account Not Active</h1>")
			
			else:
				user_info.update({'errors': "Invalid Credentials"})

				return render(request, "main/user_login.html", context = user_info)


@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('logout_thanks'))

def logout_thanks(request):
	if request.user.is_authenticated:
		# return HttpResponse("You are logged in.")
		return HttpResponseRedirect(reverse('index'))
	else:
		return render(request, "main/logout_thanks.html")

class ExpenseCreateView(LoginRequiredMixin, CreateView):
	model = models.Expense
	form_class = ExpenseCreateForm

	dictionary = { 'date': datetime.now() }
	initial = dictionary

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
		# Add in a QuerySet of the UserProfileModel
		dictionary = make_dictionary(self.request)
		context.update(dictionary)
		context.update({'ref': 'new'})
		return context

class ExpenseDetailView(LoginRequiredMixin, DetailView):
	model = models.Expense

class ExpenseListView(LoginRequiredMixin, ListView):
	# model = models.Expense
	ordering = ['-date']

	def get_queryset(self):
		e = models.Expense.objects.filter(user = self.request.user,).order_by('-date')
		# print(type(e))
		return(e)


	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
		expenses = models.Expense.objects.filter(user = self.request.user,).order_by('-date')

		expenses_json = get_expenses_in_json(expenses)
		
		# sum_dict = {}
		# Add in a QuerySet of the UserProfileModel
		dictionary = make_dictionary(self.request)
		context.update(dictionary)
		# print(type(expenses_json))
		context.update(expenses_json)
		return context

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
	form_class = ExpenseCreateForm
	model = models.Expense

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)

		context.update({'ref': 'update'})
		return context

class ExpensesSearchView(LoginRequiredMixin, ListView):
	# model = models.Expense
	ordering = ['-date']
	template_name = "main/search_result.html"

	def get_queryset(self):
		query = self.request.GET.get('query')
		print("Query: " + query)
		print("Request: " + str(self.request))

		return models.Expense.objects.filter(user = self.request.user, title__contains = query).order_by('-date')


	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
		# Add in a QuerySet of the UserProfileModel

		query = self.request.GET.get('query')

		dictionary = make_dictionary(self.request)
		context.update(dictionary)
		context.update({'query': query})
		return context

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
	model = models.Expense
	success_url = reverse_lazy('main:expense_list')

@login_required
def filter_by_date(request):

	if request.method == "POST":
		formData = FilterForm(request.POST)
		# print(formData)
		if formData.is_valid():
			start_date = formData.cleaned_data['start_date']
			end_date = formData.cleaned_data['end_date']

			# If start_date is more than end_date
			if end_date < start_date:
				dictionaryForm = { 'start_date': datetime.now(), 'end_date': datetime.now() }
				form = FilterForm(initial = dictionaryForm)

				dictionary = make_dictionary(request)
				dictionary.update({'form': form, 'error': "start_date can not be more than end_date"})
				return render(request, 'main/filterForm.html', context=dictionary)


		x = models.Expense.objects.filter(date__gte=start_date, date__lte=end_date, user = request.user).order_by('-date')

		expenses_json = get_expenses_in_json(x)

		dictionary = make_dictionary(request)
		dictionary.update({'expenses': x, 'start_date': start_date, 'end_date': end_date})

		return render(request, "main/filter_by_date.html", context = dictionary)

	else:

		# Making view searchable,search form requests GET with 3 args.
		if request.GET.get('start_date') and request.GET.get('end_date') and request.GET.get('query'):
			start_date = request.GET.get('start_date')
			end_date = request.GET.get('end_date')
			query = request.GET.get('query')

			x = models.Expense.objects.filter(date__gte=start_date, date__lte=end_date, title__icontains = query, user = request.user).order_by('-date')

			start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
			end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
			dictionary.update({'expenses': x, 'start_date': start_date, 'end_date': end_date})

			if query:
				dictionary.update({'query': query})

			return render(request, "main/filter_by_date.html", context = dictionary)

		# Else, noe search query, renser the simple form.
		else:
			dictionaryForm = { 'start_date': datetime.now(), 'end_date': datetime.now() }
			# print(dictionaryForm['start_date'])
			form = FilterForm(initial = dictionaryForm)

			dictionary = make_dictionary(request)
			dictionary.update({'form': form})

			return render(request, 'main/filterForm.html', context=dictionary)

class UserRegistration(CreateView):
	model = User
	template_name = "main/user_registration.html"
	form_class = forms.UserRegistrationForm
	success_url = reverse_lazy('main:registration_success')

	def form_valid(self, form):
		super().form_valid(form)
		username = form.cleaned_data.get('username')
		print(username)
		user = User.objects.get(username = username)
		create_code(user)

		return HttpResponseRedirect(reverse('main:registration_success'))

def registration_success(request):
	return render(request, "main/registration_success.html",)

def create_code(user):
	x = random.randint(100000, 999999)
	
	models.UserEmailConfirmation.objects.create(user = user, code = x)

@login_required
def send_email_confirmation(request):

	if request.method == "GET":
		x = models.UserEmailConfirmation.objects.get(user = request.user)

		if(x.confirmed):
			return HttpResponseRedirect(reverse("index"))

		code = x.code

		ret = send_mail(
			'Confirmation Email for ExpensesManager',
			'Your email confirmation code is: ' + str(code),
			'phasorx19@gmail.com',
			[
				# 'sonvertb19@gmail.com',
				request.user.email,
			],
			fail_silently = False,
			)

		# return HttpResponse(ret)
		return render(request, "main/confirm_email_code.html")
	elif request.method == "POST":

		code_entered = request.POST.get('code_entered')

		# Converting the recieved code into integer.
		code_entered = int(code_entered)

		x = models.UserEmailConfirmation.objects.get(user = request.user)

		if x.code == code_entered:
			x.confirmed = True
			x.save()
			return render(request, "main/confirm_email_code.html", context = {'confirmed': x.confirmed})
		else:
			return render(request, "main/confirm_email_code.html", context = {'incorrect_code': True})

