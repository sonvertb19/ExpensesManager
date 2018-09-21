from django.contrib import admin
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
	path('login/', views.user_login, name = "user_login"),
	path('register/',  views.UserRegistration.as_view(), name = "user_registration"),
	path('logout/', views.user_logout, name = "user_logout"),
	path('add/', views.ExpenseCreateView.as_view(), name = "add_expense"),
	path('add/<int:date>', views.ExpenseCreateViewWithDate.as_view(), name = "add_expense"),
	path('details/<int:pk>', views.ExpenseDetailView.as_view(), name = "expense_detail"),
	path('update/<int:pk>', views.ExpenseUpdateView.as_view(), name = "expense_update"),
	path('list/', views.ExpenseListView.as_view(), name = "expense_list"),
	path('delete/<int:pk>', views.ExpenseDeleteView.as_view(), name = "expense_delete"),
	path('special/', views.filter_by_date, name= "filter_by_date"),
	path('registration_success', views.registration_success, name = "registration_success"),
	path('search/', views.ExpensesSearchView.as_view(), name="search"),
]