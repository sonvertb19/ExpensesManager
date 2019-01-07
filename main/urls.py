from django.contrib import admin
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [

	# Registration
	path('register/',  views.UserRegistration.as_view(), name = "user_registration"),
	path('registration_success/', views.registration_success, name = "registration_success"),
	
	# Login
	path('login/', views.user_login, name = "user_login"),
	
	path('logout/', views.user_logout, name = "user_logout"),
	
	# Manage Expenses
	path('add/', views.ExpenseCreateView.as_view(), name = "add_expense"),
	path('add/<int:date>/', views.ExpenseCreateViewWithDate.as_view(), name = "add_expense"),
	path('update/<int:pk>/', views.ExpenseUpdateView.as_view(), name = "expense_update"),
	path('delete/<int:pk>/', views.ExpenseDeleteView.as_view(), name = "expense_delete"),
	path('search/', views.ExpenseListView.as_view(), name="search"),
	# path('filter/', views.ExpenseListView.as_view(), name="filter"),
	path('filter_by_date/', views.filter_by_date, name="filter_by_date"),
	path('list/', views.ExpenseListView.as_view(), name = "expense_list"),
	
	# Manage Account
	path('forgot_password/', views.ForgotPassword, name = "forgot_password"),
	path('change_password/', views.ChangePassword, name = "change_password"),
	path('password_changed/', views.password_changed, name = "password_changed"),
	path('confirm_password_reset_code', views.confirm_password_reset_code, name="confirm_password_reset_code"),
	path('reset_password/', views.reset_password, name="reset_password"),
	# JSON API for Description
	path('description/<int:pk>', views.description_api, name = 'description_api')
]