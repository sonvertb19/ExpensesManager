from builtins import print

from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import ListView, UpdateView, DetailView
from . import models
from django.urls import reverse_lazy

from main.forms import FilterForm, ExpenseCreateForm, FreshStartForm

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
# from django.contrib.auth import update_session_auth_hash

from django.db.models import Q

from django.http import JsonResponse

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt


def make_dictionary(request):
    dictionary = {}

    if request.user.is_authenticated:
        user = request.user
        x = models.UserEmailConfirmation.objects.get(user=user)
        confirmed = x.confirmed
        dictionary.update({'confirmed': confirmed})

    return dictionary


def get_expenses_in_json(expenses):
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

            date_wise_total.update({str(e.date): present_date_sum})

            if e.account:
                payment_account = e.account.title
            else:
                payment_account = ""

            present_date_expenses.update(
                {
                    e.pk: {
                        'title': e.title,
                        'date': e.date.strftime('%d-%b-%Y'),
                        'amount': e.amount,
                        'description': e.description,
                        'account': payment_account
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

            date_wise_total.update({str(e.date): present_date_sum})

            # Creating new object to record all the expenses of the new date and populating it with the first expense.
            present_date_expenses = {}

            if e.account:
                payment_account = e.account.title
            else:
                payment_account = ""

            present_date_expenses.update(
                {
                    e.pk: {
                        'title': e.title,
                        'date': e.date.strftime('%d-%b-%Y'),
                        'amount': e.amount,
                        'description': e.description,
                        'account': payment_account
                    }
                }
            )
            date_wise_expenses.update(
                {
                    str(e.date): {
                        'expenses': {}
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


def index(request):
    dictionary = make_dictionary(request)

    return render(request, "main/index.html", context=dictionary)


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    else:
        if request.method == "GET":
            return render(request, "main/user_login.html")

        elif request.method == "POST":

            # 			username = request.POST.get('uname')
            # For blue theme
            username = request.POST.get('username')

            if username:
                # password = request.POST.get('pwd')
                # For blue theme
                password = request.POST.get('password')

                if password:

                    user = authenticate(username=username, password=password)

                    user_info = {}

                    if user:
                        if user.is_active:
                            login(request, user)
                            return HttpResponseRedirect(reverse('index'))
                        else:
                            return HttpResponse("<h1>Account Not Active</h1>")

                    else:
                        user_info.update({'errors': "Invalid Credentials"})

                        return render(request, "main/user_login.html", context=user_info)

                else:
                    username_or_email = username

                    email_match = models.User.objects.filter(email=username_or_email)
                    for x in email_match:
                        email_match = x
                        first_name = email_match.first_name
                    # print(first_name)

                    if email_match:
                        username = email_match.username

                    else:
                        # Email match not found
                        username_match = models.User.objects.filter(username=username_or_email)
                        for x in username_match:
                            username_match = x
                            first_name = username_match.first_name
                        # print(first_name)

                        if username_match:
                            username = username_match.username

                        else:
                            error = "No such email or username registered."
                            return render(request, "main/user_login.html", {'errors': error})

                    return render(request, "main/user_login_enter_password.html",
                                  {'username': username, 'first_name': first_name})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = models.Category
    fields = '__all__'


class CategoryListView(LoginRequiredMixin, ListView):
    model = models.Category
    fields = '__all__'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        categories = context.get('object_list')
        categories_with_expenses = {}
        for c in categories:
            categories_with_expenses.update({
                c: c.expense_set
            })
        context['categories_with_expenses'] = categories_with_expenses
        return context

    # def get_queryset(self):
    #     # Get all categories
    #     categories = models.Category.objects.all()
    #     print(categories)


# ref == 'new'
class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = models.Expense
    form_class = ExpenseCreateForm

    def get_initial(self):
        initial = super().get_initial()
        initial.update({'date': datetime.now()})

        expense_title = self.request.GET.get('title')
        number_of_packets = self.request.GET.get('number_of_packets')

        if expense_title and number_of_packets:
            category = models.Category.objects.get(title=expense_title)
            expense_amount = int(number_of_packets) * 22
            initial.update(
                {
                    'title': expense_title,
                    'amount': expense_amount,
                    'description': number_of_packets + " packets double toned milk",
                    'category': category
                 }
            )

        vegetable_title = self.request.GET.get('vegetable_title')
        vegetable_unit_price = self.request.GET.get('vegetable_unit_price')
        vegetable_quantity = self.request.GET.get('vegetable_quantity')
        vegetable_total_amount = self.request.GET.get('vegetable_total_amount')

        if vegetable_title and vegetable_unit_price and vegetable_quantity and vegetable_total_amount:
            category = models.Category.objects.get(title="Vegetables")
            initial.update(
                {
                    'title': vegetable_title,
                    'amount': vegetable_total_amount,
                    'description': vegetable_quantity + " grams\nUnit Price: Rs " + vegetable_unit_price + " per Kg",
                    'category': category
                }
            )
        elif vegetable_title and vegetable_quantity and vegetable_total_amount:
            category = models.Category.objects.get(title="Vegetables")
            initial.update(
                {
                    'title': vegetable_title,
                    'amount': vegetable_total_amount,
                    'description': vegetable_quantity + " grams",
                    'category': category
                }
            )
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        # print(self.request.POST)
        payment_account_id = self.request.POST.get('account')
        account = models.Account.objects.get(id=payment_account_id)
        form.instance.account = account
        # print("Payment_Account_Id: " + str(payment_account_id))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of the UserProfileModel
        dictionary = make_dictionary(self.request)
        context.update(dictionary)
        payment_accounts = models.Account.objects.filter(user=self.request.user)
        context.update({'ref': 'new', 'payment_accounts': payment_accounts})
        return context


# ref == 'new' and 'date'
class ExpenseCreateViewWithDate(LoginRequiredMixin, CreateView):
    model = models.Expense
    form_class = ExpenseCreateForm

    def get_initial(self):
        initial = super().get_initial()
        date = self.kwargs.get('date')
        date = datetime.fromtimestamp(date).strftime('%Y-%m-%d')
        expense_title = self.request.GET.get('title')
        if expense_title:
            initial.update({'title': expense_title})

        expense_amount = self.request.GET.get('amount')
        if expense_amount:
            initial.update({'amount': expense_amount})

        initial.update({'date': date})
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        # print(self.request.POST)
        payment_account_id = self.request.POST.get('account')
        account = models.Account.objects.get(id=payment_account_id)
        form.instance.account = account
        # print("Payment_Account_Id: " + str(payment_account_id))
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

        payment_accounts = models.Account.objects.filter(user=self.request.user)

        # Add in a QuerySet of the UserProfileModel
        dictionary = make_dictionary(self.request)
        context.update(dictionary)
        context.update(
            {'ref': 'new', 'payment_accounts': payment_accounts, 'date': datex, 'date_in_str': str(date_str)})
        return context


# ref == 'update'
class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ExpenseCreateForm
    model = models.Expense

    def form_valid(self, form):
        # print(self.request.POST)
        payment_account_id = self.request.POST.get('account')
        account = models.Account.objects.get(id=payment_account_id)
        form.instance.account = account
        # print("Payment_Account_Id: " + str(payment_account_id))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        dictionary = make_dictionary(self.request)
        context.update(dictionary)

        payment_accounts = models.Account.objects.filter(user=self.request.user)
        current_account_pk = self.object.account.pk

        context.update(
            {'ref': 'update', 'payment_accounts': payment_accounts, 'current_account_pk': current_account_pk})
        return context


class ExpenseListView(LoginRequiredMixin, ListView):
    # model = models.Expense
    ordering = ['-date']

    def get_queryset(self):
        query = self.request.GET.get('query')
        pay_acc = self.request.GET.get('pay_acc')
        if query:
            if pay_acc:
                account_object = models.Account.objects.get(pk=pay_acc)
                return models.Expense.objects.filter((
                        Q(title__icontains=query) | Q(description__icontains=query)),
                    account=account_object, user=self.request.user, archived=False) \
                    .order_by('-date')

            return models.Expense.objects.filter((Q(title__icontains=query) | Q(description__icontains=query)),
                                                 archived=False, user=self.request.user).order_by('-date')

        else:
            if pay_acc:
                account_object = models.Account.objects.get(pk=pay_acc)
                return models.Expense.objects.filter(account=account_object, user=self.request.user).order_by('-date')

            e = models.Expense.objects.filter(user=self.request.user, archived=False).order_by('-date')
            return e

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        query = self.request.GET.get('query')
        pay_acc = self.request.GET.get('pay_acc')

        if query:
            expenses = models.Expense.objects.filter((Q(title__icontains=query) | Q(description__icontains=query)),
                                                     user=self.request.user, archived=False).order_by('-date')
            context.update({'query': query})

            if pay_acc:
                context.update({'pay_acc': pay_acc})
                account_object = models.Account.objects.get(pk=pay_acc)
                context.update({'pay_acc_name': account_object.title})
                expenses = models.Expense.objects.filter((Q(title__icontains=query) | Q(description__icontains=query)),
                                                         account=account_object, user=self.request.user,
                                                         archived=False).order_by('-date')

        # context.update(expenses_json)
        else:
            expenses = models.Expense.objects.filter(user=self.request.user, archived=False).order_by('-date')
            if pay_acc:
                context.update({'pay_acc': pay_acc})
                account_object = models.Account.objects.get(pk=pay_acc)
                context.update({'pay_acc_name': account_object.title})
                expenses = models.Expense.objects.filter(account=account_object, user=self.request.user,
                                                         archived=False).order_by('-date')

        expenses_json = get_expenses_in_json(expenses)

        grand_total = expenses_json['grand_total']

        expenses_json = json.dumps(expenses_json, sort_keys=True, indent=4)
        payment_accounts = models.Account.objects.filter(user=self.request.user)

        context.update(
            {'expenses_json': expenses_json, 'grand_total': grand_total, 'payment_accounts': payment_accounts})

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
    if request.POST.get('start_date') and request.POST.get('end_date'):
        # If start_date and end_date exists
        formData = FilterForm(request.POST)
        if formData.is_valid():
            start_date = formData.cleaned_data['start_date']
            end_date = formData.cleaned_data['end_date']
            # If start_date is more than end_date
            if end_date < start_date:
                dictionaryForm = {'start_date': datetime.now(), 'end_date': datetime.now()}
                form = FilterForm(initial=dictionaryForm)

                dictionary = make_dictionary(request)
                dictionary.update({'form': form, 'error': "'Start Date' can not be more than 'End Date"})
                return render(request, 'main/filter_by_date_form.html', context=dictionary)

            else:
                # Start and End Date OK.
                # Now check if query exists
                if request.GET.get('query'):
                    # Filter using query also.

                    query = request.GET.get('query')

                    dictionary = make_dictionary(request)
                    x = models.Expense.objects.filter((Q(title__icontains=query) | Q(description__icontains=query)),
                                                      date__gte=start_date, date__lte=end_date, user=request.user,
                                                      archived=False).order_by('-date')
                    dictionary.update({'query': request.GET.get('query')})
                else:
                    # i.e. no query
                    # Filter without query.
                    dictionary = make_dictionary(request)
                    x = models.Expense.objects.filter(date__gte=start_date, date__lte=end_date, user=request.user,
                                                      archived=False).order_by('-date')
        dictionary.update({'expense_list': x, 'start_date': start_date, 'end_date': end_date})

        expenses_json = get_expenses_in_json(x)

        grand_total = expenses_json['grand_total']

        expenses_json = json.dumps(expenses_json, sort_keys=True, indent=4)

        dictionary.update({'expenses_json': expenses_json, 'grand_total': grand_total})

        return render(request, "main/filter_by_date_result.html", context=dictionary)


    else:
        # No start_date and end_date exists.
        # i.e. Page opened to see form.
        dictionaryForm = {'start_date': datetime.now(), 'end_date': datetime.now()}
        form = FilterForm(initial=dictionaryForm)

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
        user = User.objects.get(username=username)
        create_or_update_code(user)
        models.Account.objects.create(user=user, title="Cash")
        models.Account.objects.create(user=user, title="Paytm")
        models.Account.objects.create(user=user, title="Bank Account")

        return HttpResponseRedirect(reverse('main:registration_success'))


def registration_success(request):
    return render(request, "main/registration_success.html", )


def create_or_update_code(user):
    x = random.randint(100000, 999999)

    try:
        user_email_confirmation = models.UserEmailConfirmation.objects.get(user=user)

        # if object exists, update the code.
        user_email_confirmation.code = x
        user_email_confirmation.save()

    except ObjectDoesNotExist:
        models.UserEmailConfirmation.objects.create(user=user, code=x, confirmed=False)


@login_required
def send_email_confirmation(request):
    if request.method == "GET":
        create_or_update_code(request.user)
        x = models.UserEmailConfirmation.objects.get(user=request.user)

        if x.confirmed:
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
            fail_silently=False,
        )

        # return HttpResponse(ret)
        return render(request, "main/confirm_email_code.html")
    elif request.method == "POST":

        code_entered = request.POST.get('code_entered')

        # Converting the recieved code into integer.
        code_entered = int(code_entered)

        x = models.UserEmailConfirmation.objects.get(user=request.user)

        if x.code == code_entered:
            x.confirmed = True
            x.save()
            return render(request, "main/confirm_email_code.html", context={'confirmed': x.confirmed})
        else:
            return render(request, "main/confirm_email_code.html", context={'incorrect_code': True})


def ForgotPassword(request):
    if request.method == "GET":
        return render(request, "main/forgot_password.html")

    if request.method == "POST":
        email_or_username = request.POST.get('email_or_username')

        email_match = models.User.objects.filter(email=email_or_username)
        for x in email_match:
            email_match = x

        if email_match:
            # Email Match Found
            create_or_update_code(email_match)

            x = models.UserEmailConfirmation.objects.get(user=email_match)
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
                fail_silently=False,
            )

            email = email_match.email

            return render(request, "main/forgot_password_email_or_username_match.html",
                          context={'message': "Hurray, we found a matching account!", 'message_color': 'green',
                                   'email_code_sent': 'true', 'email': email})
        else:
            # Email match not found
            username_match = models.User.objects.filter(username=email_or_username)
            for x in username_match:
                username_match = x

            if username_match:
                # Username Match Found

                create_or_update_code(username_match)

                x = models.UserEmailConfirmation.objects.get(user=username_match)
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
                    fail_silently=False,
                )

                email = username_match.email

                return render(request, "main/forgot_password_email_or_username_match.html",
                              context={'message': "Hurray, we found a matching account!", 'message_color': 'green',
                                       'email_code_sent': 'true', 'email': email})
            else:
                # Username match not Found
                # No match found
                return render(request, "main/forgot_password.html", context={
                    'message': "Oops! We cound not find any email or username in our records. Please try again!",
                    'message_color': 'red'})


# Carried from def ForgotPassword
def confirm_password_reset_code(request):
    # Only POST is method is accepted.
    if request.method == "POST":

        email = request.POST.get('email')

        code_entered = request.POST.get('code_entered')

        u = models.User.objects.get(email=email)

        email = str(u.email)

        x = models.UserEmailConfirmation.objects.get(user=u)

        if x.code == int(code_entered):
            # Show password Reset Page.
            return render(request, "main/reset_password.html", context={'email': email})
        else:
            # Invalid Password reset code.
            return render(request, "main/forgot_password_email_or_username_match.html",
                          context={'incorrect_code': True, 'email': email})
    # return HttpResponse("Test OK")

    else:
        # If method is not POST
        # return HttpResponse("<h3>Invalid request method, Only POST accepted.</h3>")
        return HttpResponse(status=405, content="<h3> 405 - METHOD NOT ALLOWED </h3> <p>Only POST allowed</p>")


# Carried from def confirm_password_reset_code
def reset_password(request):
    context = {}

    # Only POST is method is accepted.
    if request.method == "POST":

        email = request.POST.get('email')

        u = models.User.objects.get(email=email)

        new_password = request.POST.get('pass1')
        confirm_new_password = request.POST.get('pass2')

        if new_password != confirm_new_password:

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
        # return HttpResponse("<h3>Invalid request method, Only POST accepted.</h3>")
        return HttpResponse(status=405, content="<h3> 405 - METHOD NOT ALLOWED </h3> <p>Only POST allowed</p>")


@login_required
def ChangePassword(request):
    if request.method == "GET":
        a = request.GET.get('a')
        context = {'a': a}

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

            context.update({'error': "New passwords do not match."})

            return render(request, "main/change_password.html", context)

        elif check_password(current_password, request.user.password):
            # If password matches succesfully.
            request.user.set_password(new_password)
            request.user.save()
            # update_session_auth_hash(request, request.user.password)

            return HttpResponseRedirect(reverse('main:password_changed'))

        else:

            context.update({'error': "Invalid Current Password"})

            return render(request, "main/change_password.html", context)


@login_required
def description_api(request, **kwargs):
    pk = kwargs.get('pk')

    e = models.Expense.objects.get(pk=pk)

    d = e.description

    d = d.replace("\n", "<br/>")

    if e.user == request.user:
        return JsonResponse({"pk": pk, "description": d})
    else:
        return JsonResponse({"error_code": "Error 403", "error_descrition": "Unauthorised User"})


@csrf_exempt
def alexa_add_expenses_without_login(request, **kwargs):
    print(request)
    print(request.POST)

    if request.method == 'GET':
        return JsonResponse({'message': "GET requests not allowed"}, status=405)

    title = request.POST["title"]
    amount = request.POST["amount"]
    date = request.POST["date"]
    
    parsed_date = datetime.strptime(date, "%Y-%m-%d")
    print(parsed_date)

    alexa_category = models.Category.objects.get(title="ADDED_USING_ALEXA")
    home_user = models.User.objects.get(username="bhardwaj_home")
    cash_account = models.Account.objects.get(title="Cash",user=home_user)

    expense = models.Expense.objects.create(title=title,
                                            amount=amount,
                                            date=parsed_date,
                                            category=alexa_category,
                                            user=home_user,
                                            account=cash_account)

    expense.save()

    return JsonResponse({'message': "OK"}, status=200)


def password_changed(request):
    return render(request, 'main/password_changed.html')


@login_required
def FreshStart(request):
    if request.method == "POST":
        form_data = FreshStartForm(request.POST)
        if form_data.is_valid():
            fresh_start_date = form_data.cleaned_data['fresh_start_date']
            date = fresh_start_date.strftime('%d %b %Y')

            e = models.Expense.objects.filter(date__lt=fresh_start_date, user=request.user)

            total_expenses_arcihved = 0
            total_amount = 0

            for x in e:
                total_amount = total_amount + x.amount
                total_expenses_arcihved = total_expenses_arcihved + 1

                x.archived = True
                x.save()

            return render(request, 'main/fresh_start.html', {'fresh_start_completed': True, 'date': date,
                                                             'total_expenses_arcihved': total_expenses_arcihved,
                                                             'total_amount': total_amount})

        # return HttpResponse('<h5>Date: ' + str(fresh_start_date) + '</h5>' + '<h5>' + str(total_expenses_arcihved) + ' expenses archived worth Rs ' + str(total_amount) + '</h5>')
    else:
        return render(request, 'main/fresh_start.html')
    # return HttpResponse(status=405, content="<h3> 405 - METHOD NOT ALLOWED </h3> <p>Only POST allowed</p>")

# if request.POST.get('fresh_start_date'):

#     return HttpResponse('<h5>date: ' + request.POST.get('fresh_start_date') + '</h5>')

# return HttpResponseRedirect(reverse('index'))
