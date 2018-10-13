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

from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash

from django.db.models import Q

from django.http import JsonResponse

def make_dictionary(request):

	dictionary = {}

	if request.user.is_authenticated:
	
		user = request.user
		x = models.UserEmailConfirmation.objects.get(user = user)

		confirmed = x.confirmed
		dictionary.update({'confirmed': confirmed})

	return dictionary

def get_expenses_in_json(expenses):

	prev_date = 0;

	date_wise_expenses = {}
	present_date_expenses = {}
	list_of_dates = []
	date_wise_total = {}

	grand_total = 0
	present_date_sum = 0

	for e in expenses:
		if str(e.date) in list_of_dates:
			# Date exists in list of dates, i.e. this is NOT the first expense of this date.

			present_date_sum = present_date_sum + e.amount

			grand_total = grand_total + e.amount

			date_wise_total.update({ str(e.date): present_date_sum })

			present_date_expenses.update(
											{
												e.pk: {
														'title': e.title,
														'amount': e.amount,
														'description': e.description
													}
											}
										)

			date_wise_expenses[str(e.date)]['expenses'].update(present_date_expenses)

		else:
			# Date exists in list of dates, i.e. this is the first expense of this date.
			# It also means that a previous date's expenses ended.



			list_of_dates.append(str(e.date))


			# Initializing the present_date_sum and adding the amount of first expense.
			present_date_sum = 0
			present_date_sum = present_date_sum + e.amount

			# Adding to the grand total
			grand_total = grand_total + e.amount

			date_wise_total.update({ str(e.date): present_date_sum })

			# Creating new object to record all the expenses of the new date and populating it with the first expense.
			present_date_expenses = {}

			present_date_expenses.update(
											{
												e.pk: {
														'title': e.title,
														'amount': e.amount,
														'description': e.description
													}
											}
										)
			date_wise_expenses.update(
										{
											str(e.date): {
												'expenses' : {}
											}
										}
									)

			date_wise_expenses[str(e.date)]['expenses'].update(present_date_expenses)

	# date_wise_expenses = json.dumps(date_wise_expenses, sort_keys=True, indent=4)
	# date_wise_total = json.dumps(date_wise_total, sort_keys=True, indent=4)
	
	grouped_expenses_json = {
								'date_wise_expenses': date_wise_expenses,
								'date_wise_total': date_wise_total,
								'grand_total': grand_total
							}

	return grouped_expenses_json

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

# ref == 'new'
class ExpenseCreateView(LoginRequiredMixin, CreateView):
	model = models.Expense
	form_class = ExpenseCreateForm

	# dictionary = { 'date': datetime.now() }
	# initial = dictionary

	def get_initial(self):
		initial = super().get_initial()
		initial.update({ 'date': datetime.now() })
		return initial

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

# ref == 'new' and 'date'
class ExpenseCreateViewWithDate(LoginRequiredMixin, CreateView):
	model = models.Expense
	form_class = ExpenseCreateForm

	# dictionary = { 'date': date }
	# initial = dictionary

	def get_initial(self):
		initial = super().get_initial()

		date = self.kwargs.get('date')

		print(datetime.now())
		date = datetime.fromtimestamp(date).strftime('%Y-%m-%d')

		print(date)

		initial.update({ 'date': date })
		return initial

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super().form_valid(form)

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
		
		date = self.kwargs.get('date')
		# print(type(date))
		datex = datetime.fromtimestamp(date)

		# print(datex)

		date_str = datetime.strptime(str(datex), "%Y-%m-%d %H:%M:%S")

		# print(date_str)

		# Add in a QuerySet of the UserProfileModel
		dictionary = make_dictionary(self.request)
		context.update(dictionary)
		context.update({'ref': 'new', 'date': datex, 'date_in_str': str(date_str) })
		return context

# ref == 'update'
class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
	form_class = ExpenseCreateForm
	model = models.Expense

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)

		dictionary = make_dictionary(self.request)
		context.update(dictionary)

		context.update({'ref': 'update'})
		return context

class ExpenseListView(LoginRequiredMixin, ListView):
	# model = models.Expense
	ordering = ['-date']

	def get_queryset(self):

		query = self.request.GET.get('query')

		if query:
			return models.Expense.objects.filter((Q(title__icontains = query) | Q(description__icontains = query)), user = self.request.user).order_by('-date')

		else:

			e = models.Expense.objects.filter(user = self.request.user,).order_by('-date')
			return(e)


	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)

		query = self.request.GET.get('query')

		if query:
			expenses = models.Expense.objects.filter((Q(title__icontains = query) | Q(description__icontains = query)), user = self.request.user).order_by('-date')
			context.update({'query': query})

			# context.update(expenses_json)
		else:
			expenses = models.Expense.objects.filter(user = self.request.user,).order_by('-date')

		expenses_json = get_expenses_in_json(expenses)

		grand_total = expenses_json['grand_total']

		expenses_json = json.dumps(expenses_json, sort_keys=True, indent=4)

		context.update({'expenses_json': expenses_json, 'grand_total': grand_total})

		dictionary = make_dictionary(self.request)

		context.update(dictionary)

		return context

class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
	model = models.Expense
	success_url = reverse_lazy('main:expense_list')

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)

		dictionary = make_dictionary(self.request)

		context.update(dictionary)

		return context

	# Added to avoid confirmation page.
	def get(self, request, *args, **kwargs):
		return self.post(request, *args, **kwargs)

@login_required
def filter_by_date(request):

	if request.GET.get('start_date') and request.GET.get('end_date'):
		# If start_date and end_date exists
		formData = FilterForm(request.GET)
		print(formData)
		if formData.is_valid():
			start_date = formData.cleaned_data['start_date']
			end_date = formData.cleaned_data['end_date']

			print("data cleaned")

			# If start_date is more than end_date
			if end_date < start_date:
				dictionaryForm = { 'start_date': datetime.now(), 'end_date': datetime.now() }
				form = FilterForm(initial = dictionaryForm)

				print("start date greater error")


				dictionary = make_dictionary(request)
				dictionary.update({'form': form, 'error': "'Start Date' can not be more than 'End Date"})
				return render(request, 'main/filter_by_date_form.html', context=dictionary)

			else:
			# Start and End Date OK.
				print("Start and End Date OK.")
				# Now check if query exists
				if request.GET.get('query'):
					# Filter using query also.
					
					query = request.GET.get('query')
					print("query exists")

					dictionary = make_dictionary(request)
					x = models.Expense.objects.filter((Q(title__icontains = query) | Q(description__icontains = query)), date__gte=start_date, date__lte=end_date, user = request.user).order_by('-date')
					dictionary.update({'query': request.GET.get('query')})
				else:
					# i.e. no query
					# Filter without query.
					print("query does not exist")
					dictionary = make_dictionary(request)
					x = models.Expense.objects.filter(date__gte=start_date, date__lte=end_date, user = request.user).order_by('-date')

		print(start_date)
		print(end_date)
		dictionary.update({'expense_list': x, 'start_date': start_date, 'end_date': end_date})

		expenses_json = get_expenses_in_json(x)

		grand_total = expenses_json['grand_total']

		expenses_json = json.dumps(expenses_json, sort_keys=True, indent=4)

		dictionary.update({'expenses_json': expenses_json, 'grand_total': grand_total})

		return render(request, "main/filter_by_date_result.html", context = dictionary)


	else:
		# No start_date and end_date exists.
		# i.e. Page opened to see form.
		dictionaryForm = { 'start_date': datetime.now(), 'end_date': datetime.now() }
		form = FilterForm(initial = dictionaryForm)

		dictionary = make_dictionary(request)
		dictionary.update({'form': form})

		return render(request, 'main/filter_by_date_form.html', context=dictionary)

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
	
	print(user)
	print(type(user))

	s = models.UserEmailConfirmation.objects.get(user = user)
	s.code = x
	s.save()

@login_required
def send_email_confirmation(request):

	if request.method == "GET":
		create_code(request.user)
		x = models.UserEmailConfirmation.objects.get(user = request.user)

		if(x.confirmed):
			return HttpResponseRedirect(reverse("index"))

		code = x.code

		ret = send_mail(
			'Confirmation Email for ExpensesManager',
			'Hi, ' + request.user.first_name + ' ' +
			'Thank you for trying out the website! ' +
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

def create_code_password_reset(user):
	x = random.randint(100000, 999999)
	
	print(user)
	print(type(user))

	s = models.UserEmailConfirmation.objects.get(user = user)
	s.code = x
	s.save()

def ForgotPassword(request):

	if request.method == "GET":
		return render(request, "main/forgot_password.html")

	if request.method == "POST":
		email_or_username = request.POST.get('email_or_username')

		email_match = models.User.objects.filter(email = email_or_username)
		for x in email_match:
			email_match = x

		if email_match:
			# Email Match Found
			print("email match")
			print(email_match)

			create_code_password_reset(email_match)

			x = models.UserEmailConfirmation.objects.get(user = email_match)
			code = x.code

			ret = send_mail(
				'Password Reset Code Expenses Manager',
				'Hi, ' + email_match.first_name + ' ' +
				'We have recieved a request for resetting your password.' +
				'Your password reset code is: ' + str(code) + "",
				'phasorx19@gmail.com',
				[
					# 'sonvertb19@gmail.com',
					email_match.email,
				],
				fail_silently = False,
				)

			email = email_match.email
			print("Email found in email match: " + str(email))

			return render(request, "main/forgot_password_email_or_username_match.html", context={'message': "Hurray, we found a matching account!", 'message_color': 'green', 'email_code_sent': 'true', 'email': email})
		else:
			# Email match not found
			username_match = models.User.objects.filter(username = email_or_username)
			for x in username_match:
				username_match = x

			if username_match:
				# Username Match Found
				print("username match")
				print(username_match)

				create_code_password_reset(username_match)

				x = models.UserEmailConfirmation.objects.get(user = username_match)
				code = x.code

				ret = send_mail(
					'Password Reset Code Expenses Manager',
					'Hi, ' + username_match.first_name + ' ' +
					'We have recieved a request for resetting your password.' +
					'Your password reset code is: ' + str(code) + "",
					'phasorx19@gmail.com',
					[
						# 'sonvertb19@gmail.com',
						username_match.email,
					],
					fail_silently = False,
					)

				email = username_match.email
				print("Email found in username match: " + str(email))

				return render(request, "main/forgot_password_email_or_username_match.html", context={'message': "Hurray, we found a matching account!", 'message_color': 'green', 'email_code_sent': 'true', 'email': email})
			else:
				# Username match not Found
				# No match found
				return render(request, "main/forgot_password.html", context={'message': "Oops! We cound not find any email or username in our records. Please try again!", 'message_color': 'red'})

# Carried from def ForgotPassword
def confirm_password_reset_code(request):

	# Only POST is method is accepted.
	if request.method == "POST":

		email = request.POST.get('email')
		print("Email catched in confirm_password_reset_code: " + str(email))

		print(type(email))
		print(email)

		code_entered = request.POST.get('code_entered')
		
		print("Code recieved from POST: " + str(code_entered))

		u = models.User.objects.get(email = email)

		print("User found from email: " + str(u))
		
		email = str(u.email)

		print("Email found from user: " + str(email))

		x = models.UserEmailConfirmation.objects.get(user = u)

		print("Confirmation Code from database: " + str(x.code))

		print("type of x.code = " + str(type(x.code)))



		if x.code == int(code_entered):
			# Show password Reset Page.
			return render(request, "main/reset_password.html", context = {'email': email})
		else:
			# Invalid Password reset code.
			return render(request, "main/forgot_password_email_or_username_match.html", context = {'incorrect_code': True, 'email': email})	
		# return HttpResponse("Test OK")

	else:
		# If method is not POST
		return HttpResponse("<h3>Invalid request method, Only POST accepted.</h3>")

# Carried from def confirm_password_reset_code
def reset_password(request):

	context = {}

	# Only POST is method is accepted.
	if request.method == "POST":

		email = request.POST.get('email')

		u = models.User.objects.get(email = email)
		
		new_password = request.POST.get('pass1')
		confirm_new_password = request.POST.get('pass2')
		
		if new_password != confirm_new_password:
			print("PASSWORDS DO NOT MATCH")

			context.update({'error': "Entered passwords do not match.", 'email': email})

			return render(request, "main/reset_password.html", context=context)

		else:
			# If password matches succesfully.

			u.set_password(new_password)
			u.save()
			# update_session_auth_hash(request, request.user.password)

			return HttpResponseRedirect(reverse('main:password_changed'))

	else:
		# If method is not POST
		return HttpResponse("<h3>Invalid request method, Only POST accepted.</h3>")	

@login_required
def ChangePassword(request):

	if request.method == "GET":
		a = request.GET.get('a')
		context={'a': a}

		dictionary = make_dictionary(request)
		context.update(dictionary)

		return render(request, "main/change_password.html", context)
	
	elif request.method == "POST":

		context = {}

		dictionary = make_dictionary(request)
		context.update(dictionary)

		current_password = request.POST.get('pass1')
		new_password = request.POST.get('pass2')
		confirm_new_password = request.POST.get('pass3')

		if new_password != confirm_new_password:
			print("PASSWORDS DO NOT MATCH")

			context.update({'error': "New passwords do not match."})

			return render(request, "main/change_password.html", context)

		elif check_password(current_password, request.user.password):
			# If password matches succesfully.
			request.user.set_password(new_password)
			request.user.save()
			# update_session_auth_hash(request, request.user.password)

			return HttpResponseRedirect(reverse('main:password_changed'))

		else:
			print("Else")

			context.update({'error': "Invalid Current Password"})

			return render(request, "main/change_password.html", context)

@login_required
def description_api(request, **kwargs):

	pk = kwargs.get('pk')

	e = models.Expense.objects.get(pk = pk)

	d = e.description

	d = d.replace("\n", "<br/>")

	if e.user == request.user:
		return JsonResponse({"pk": pk, "description": d})
	else:
		return JsonResponse({"error_code": "Error 403", "error_descrition": "Unauthorised User"})

def password_changed(request):
	return render(request, 'main/password_changed.html')