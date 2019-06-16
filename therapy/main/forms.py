import datetime

from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

from .models import *


class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')


class PatientForm(forms.ModelForm):
	class Meta:
		model = Patient
		fields = ('categories', 'gender', 'birthdate', 'bio')

		categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all())
		widgets = {
			'birthdate' : DatePicker(
				options={
				'mixDate': '1900-01-01',
				'maxDate': '2019-05-01'}, 
				attrs={
				'append' : 'fa fa-calendar',
				'icon_toggle': True},)
			}

	def __init__(self, *args, **kwargs):
		if kwargs.get('instance'):
			initial = kwargs.setdefault('initial', {})
			initial['categories'] = [cat.pk for cat in kwargs['instance'].categories.all()]
		forms.ModelForm.__init__(self, *args, **kwargs)

	def save(self):
		instance = forms.ModelForm.save(self)
		instance.categories.clear()
		instance.categories.add(*self.cleaned_data['categories'])
		return instance


class TherapistForm(forms.ModelForm):
	class Meta:
		model = Therapist
		fields = ('address', 'experience', 'education', 'languages', 'categories', 'gender', 'birthdate', 'bio', 'working_days', 'working_hours')
		
		categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all())
		working_days = forms.ModelMultipleChoiceField(
				queryset=Day.objects.all(),
				widget=forms.CheckboxSelectMultiple
				)

		working_hours = forms.ModelMultipleChoiceField(
				queryset=Hour.objects.all(),
				widget=forms.CheckboxSelectMultiple
				)
		
		widgets = {
			'birthdate' : DatePicker(
				options={
				'mixDate': '1900-01-01',
				'maxDate': '2019-05-01'}, 
				attrs={
				'append' : 'fa fa-calendar',
				'icon_toggle': True},) 
			}

	def __init__(self, *args, **kwargs):
		if kwargs.get('instance'):
			initial = kwargs.setdefault('initial', {})
			initial['categories'] = [cat.pk for cat in kwargs['instance'].categories.all()]
		forms.ModelForm.__init__(self, *args, **kwargs)

	def save(self):
		instance = forms.ModelForm.save(self)
		instance.categories.clear()
		instance.categories.add(*self.cleaned_data['categories'])
		return instance


class CustomUserCreationForm(UserCreationForm):
	class Meta:
		model = get_user_model()
		fields = ('username', 'email')


# class ImageForm(forms.ModelForm):
#     class Meta:
#         model= Image
#         fields= ["name", "imagefile"]


class TherapistSessionLogForm(forms.ModelForm):
	class Meta:
		model=SessionLog
		fields=("therapist_notes",)