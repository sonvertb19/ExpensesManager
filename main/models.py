from django.db import models
from django.urls import reverse
# Create your models here.
class Expense(models.Model):
	title = models.CharField(max_length = 200)
	amount = models.PositiveIntegerField()
	date = models.DateField()

	def __str__(self):
		return self.title

	def new(self):
		return self.amount

	def get_absolute_url(self):
		return reverse("main:expense_list")