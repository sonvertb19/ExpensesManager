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

from django.db.models import Q

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
	# Expenses here are already sorted.

	# month_names = ["January", "February", "March", 
	# 		"April", "May", "June", "July", "August", "September", 
	# 		"October", "November", "December"]

	prev_date = 0;
	# prev_month = 0;
	# current_month = 0;

	# current_month_total = 0


	date_wise_expenses = {}
	grouped_expenses = {}
	list_of_dates = []
	# list_of_months = []
	date_wise_total = {}
	# month_wise_total = []
	
	index = -1
	
	# Creating list of months.
	# for e in expenses:

	# 	# Usng index so that the first 'new_month' : 0 is not added to month_wise_total.
	# 	index = index  + 1
	# 	prev_month_str = str(prev_month)
	# 	current_month = e.date.month

	# 	if(str(current_month) in list_of_months):
	# 		current_month_total = current_month_total + e.amount
	# 		# print( str(e.date) + " - " + str(e.amount) )
	# 		# print("current_month_total = " + str(current_month_total))
	# 		pass
	# 	else:
	# 		#New month Found.
	# 		# print("#######New Month Found.########")

	# 		#Add it to the list of months.
	# 		list_of_months.append(str(current_month))
	# 		# print(list_of_months)

	# 		#Update the monthly total dictionary.
	# 		if index == 0:
	# 			pass
	# 		else:
	# 			month_wise_total.append(
	# 										{
	# 			#Current month will not work here because this code executes...
	# 			# ...when the month have changed.
	# 											'month': str(month_names[current_month]),
	# 											'amount': current_month_total
	# 										}
	# 									)

	# 		# print(month_wise_total)

	# 		#Reset current_month_total variable
	# 		current_month_total = 0

	# 		#Update Previous month
	# 		prev_month = current_month

	# #Updating the last month's expenses.
	# month_wise_total.append(
	# 							{
	# #here the current month is same, hrnce no +1.
	# 							'month': str(month_names[current_month - 1]),
	# 							'amount': current_month_total
	# 							}
	# 						)

	# # print(list_of_months)
	# # print(month_wise_total)

	for e in expenses:
		prev_date_str = str(prev_date)
		current_date = e.date

		if(str(current_date) in date_wise_expenses):
			# print(str(current_date) + " exists in grouped_expenses.")
			pass
		else:
			# Updating dictionary with key as date_name and value as a dictionary an empty-array with its key as expenses.
			date_wise_expenses.update(	
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
		current_expense_dictionary = { 'title': e.title, 'amount': e.amount, 'description': e.description}

		# print(current_expense_dictionary)

		# Updating the date dictionary with current expense dictionary.
		date_wise_expenses[str(current_date)]['expenses'].append( current_expense_dictionary )
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

	# print(date_wise_expenses)



	grand_total = 0
	for d in date_wise_expenses:
		# Indexing date wise
		# print(d)

		sum_e = 0
		current_expense_list = date_wise_expenses[d]['expenses']
		for e in current_expense_list:
			# Indexing expenses wise
			sum_e = sum_e + e['amount']
			grand_total = grand_total + e['amount']

		# print("Sum = " + str(sum_e))
		current_sum_dict = { str(d) : sum_e}

		date_wise_total.update(current_sum_dict)

	sum_dict_json = json.dumps(date_wise_total, sort_keys=True, indent=4)

	# print(sum_dict_json)

	grouped_expenses.update(
								{
									'date_wise_expenses': date_wise_expenses,
									'date_wise_total': date_wise_total,
									'grand_total': grand_total,
									# 'month_wise_total': month_wise_total,
									# 'list_of_months': list_of_months,
									'list_of_dates': list_of_dates
								}
							)
	
	grouped_expenses_json = json.dumps(grouped_expenses, sort_keys=True, indent=4)
	
	print(grouped_expenses_json)
	# print(month_names)

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

class ExpenseCreateViewWithDate(LoginRequiredMixin, CreateView):
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
		
		date = self.kwargs.get('date')
		# print(type(date))
		datex = datetime.fromtimestamp(date)

		print(datex)

		date_str = datetime.strptime(str(datex), "%Y-%m-%d %H:%M:%S")

		print(date_str)

		# Add in a QuerySet of the UserProfileModel
		dictionary = make_dictionary(self.request)
		context.update(dictionary)
		context.update({'ref': 'new', 'date': date, 'date_in_str': str(date_str) })
		return context

class ExpenseDetailView(LoginRequiredMixin, DetailView):
	model = models.Expense

class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
	form_class = ExpenseCreateForm
	model = models.Expense

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)

		context.update({'ref': 'update'})
		return context

class ExpenseListView(LoginRequiredMixin, ListView):
	# model = models.Expense
	ordering = ['-date']

	def get_queryset(self):

		query = self.request.GET.get('query')

		if query:
			print("Query: " + query)
			print("Request: " + str(self.request))
			return models.Expense.objects.filter((Q(title__icontains = query) | Q(description__icontains = query)), user = self.request.user).order_by('-date')

		else:

			e = models.Expense.objects.filter(user = self.request.user,).order_by('-date')
			# print(type(e))
			return(e)


	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)

		query = self.request.GET.get('query')

		if query:
			print("Query: " + query)
			print("Request: " + str(self.request))
			expenses = models.Expense.objects.filter((Q(title__icontains = query) | Q(description__icontains = query)), user = self.request.user).order_by('-date')
			context.update({'query': query})

		else:
			expenses = models.Expense.objects.filter(user = self.request.user,).order_by('-date')

		expenses_json = get_expenses_in_json(expenses)
		
		# sum_dict = {}
		# Add in a QuerySet of the UserProfileModel
		dictionary = make_dictionary(self.request)
		
		context.update(dictionary)

		context.update(expenses_json)
		return context

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
	model = models.Expense
	success_url = reverse_lazy('main:expense_list')


	# Added to avoid confirmation page.
	def get(self, request, *args, **kwargs):
		return self.post(request, *args, **kwargs)

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

