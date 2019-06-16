import datetime

from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

class Day(models.Model):
	name = models.CharField(max_length=20)
	daycode = models.IntegerField(null=True)

	def __str__(self):
		return f"{self.name}"

class Hour(models.Model):
	name = models.IntegerField()

	def __str__(self):
		return f"{self.name}"

class User(AbstractUser):
	is_patient = models.BooleanField(default=True)

class Category(models.Model):
	name = models.CharField(max_length=30)

	def __str__(self):
		return f"{self.name}"

class Therapist(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	address = models.TextField(null=True)
	experience = models.IntegerField(null=True)
	education = models.CharField(max_length=30, null=True)
	languages = models.CharField(max_length=30, null=True)
	categories = models.ManyToManyField(Category)
	gender = models.CharField(max_length=30, null=True)
	birthdate = models.DateField(null=True)
	bio = models.TextField(null=True)
	working_days = models.ManyToManyField(Day)
	working_hours = models.ManyToManyField(Hour)
	picture = models.ImageField(upload_to='media/images/',default=None, null=True, blank=True)


class Patient(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	categories = models.ManyToManyField(Category)
	gender = models.CharField(max_length=30, null=True)
	birthdate = models.DateField(null=True)
	bio = models.TextField(null=True)
	picture = models.ImageField(upload_to='media/images/',default=None, null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if instance.is_patient:
		Patient.objects.get_or_create(user = instance)
	else:
		Therapist.objects.get_or_create(user = instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	if instance.is_patient:
		instance.patient.save()
	else:
		Therapist.objects.get_or_create(user = instance)


class TherapySession(models.Model):
	datetime = models.DateTimeField()
	occured = models.BooleanField(null=True)
	therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, null=True)
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)


class SessionLog(models.Model):
	therapist_notes = models.TextField(null=True)
	patient_notes = models.TextField(null=True)
	therapysession = models.ForeignKey(TherapySession, on_delete=models.SET_NULL, null=True)


class Chat(models.Model):
	patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
	therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)

	def get_unread_count_patient(self):
		return Message.objects.filter(chat=self, read=False, user=self.therapist.user).count()
	
	def get_unread_count_therapist(self):
		return Message.objects.filter(chat=self, read=False, user=self.patient.user).count()

class Message(models.Model):
	content = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(default=timezone.now)
	read = models.BooleanField(default=False)


# class Image(models.Model):
#     name= models.CharField(max_length=500)
#     imagefile= models.FileField(upload_to='images/', null=True, verbose_name="")

#     def __str__(self):
#         return self.name + ": " + str(self.imagefile)