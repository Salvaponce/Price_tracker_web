from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey, OneToOneField

class Report(models.Model):
    title = models.CharField(max_length=150)
    user = ForeignKey(User, on_delete=models.CASCADE)

class Product(models.Model):
    data = models.CharField(max_length=300)
    report = ForeignKey(Report, on_delete=models.CASCADE)

class Feedback(models.Model):
    name = models.CharField(max_length=200, help_text="Name of the sender")
    email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Feedback"

    def __str__(self):
        return self.name + "-" +  self.email
