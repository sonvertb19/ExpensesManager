from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import DetailView, ListView
from . import models
from django.urls import reverse_lazy

from main.forms import FilterForm, ExpenseCreateForm

from datetime import datetime

from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin

from main import forms

def Index(request):
	return render(request, "main/index.html")

def user_login(request):

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

# class ExpenseDetailView(LoginRequiredMixin, DetailView):
# 	model = models.Expense

class ExpenseListView(LoginRequiredMixin, ListView):
	# model = models.Expense
	ordering = ['-date']

	def get_queryset(self):
		return models.Expense.objects.filter(user = self.request.user).order_by('-date')

# class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
# 	model = models.Expense
# 	success_url = reverse_lazy('main:expense_list')

@login_required
def filter_by_date(request):

	if request.method == "POST":
		formData = FilterForm(request.POST)
		print(formData)
		if formData.is_valid():
			start_date = formData.cleaned_data['start_date']
			end_date = formData.cleaned_data['end_date']


		x = models.Expense.objects.filter(date__gte=start_date, date__lte=end_date, user = request.user).order_by('-date')

		total = 0
		for e in x:
			total = total + e.amount

		return render(request, "main/filter_by_date.html", context = {'expenses': x, 'start_date': start_date, 'end_date': end_date, 'total': total})

	else:
		dictionary = { 'start_date': datetime.now(), 'end_date': datetime.now() }
		form = FilterForm(initial = dictionary)
		return render(request, 'main/filterForm.html', context={'form': form})

def user_registration(request):

	if request.method == "GET":
		if request.user.is_authenticated:
			return render(request, "main/logged_in_registration.html")

		registered = False

		userBasicForm = forms.userBasicForm()

		return render(request, 'main/user_registration.html',
					   {'userBasicForm': userBasicForm,
					   	'registered': registered
					   })

	elif request.method == 'POST':

		userBasicForm = forms.userBasicForm(request.POST)
		print(request.POST)

		registered = False

		if userBasicForm.is_valid():
			
			uBF = userBasicForm.save(commit = False)
			uBF.set_password(uBF.password)
			uBF.save()

			print(request.POST)
			registered = True
		else:
			print(str(userBasicForm.errors) + "\n\n" +str(userProfileForm.errors))

		return render(request, 'main/user_registration.html',{'registered': registered})