from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Expense(models.Model):

	title = models.CharField(max_length = 200)
	amount = models.PositiveIntegerField()
	date = models.DateField()
	user = models.ForeignKey(User, on_delete = models.CASCADE, null = True)

	def __str__(self):
		return self.title

	def new(self):
		return self.amount

	def get_absolute_url(self):
		return reverse("main:expense_list")

class UserEmailConfirmation(models.Model):
	
	user = models.ForeignKey(User, on_delete = models.CASCADE, null = True)
	code = models.PositiveIntegerField()
	confirmed = models.BooleanField(default = False)

	def __str__(self):
		return self.user.username

class Group(models.Model):
	name = models.CharField(max_length = 200)
	user_requests = models.ManyToManyField(User, related_name = "requested_groups", blank = True)
	user_approved = models.ManyToManyField(User, related_name = "approved_groups", blank = True)

	def __str__(self):
		return self.name

	def approve_user(self, user):
		u = self.user_requests.get(username = user.username)
		self.user_approved.add(u)

		self.user_requests.get(username = user.username).delete()

		self.save()

# class Member(models.Model):

