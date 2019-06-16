import os
import random
import django
from faker import Faker
from datetime import date, datetime, timedelta
from django.utils import timezone


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'therapy.settings')

django.setup()

from main.models import *

fake = Faker()

def gen_fname():
	return fake.first_name()


def date_list(start_date=timezone.now(), delta=timedelta(days=1)):
	end_date = (start_date + timedelta(days=60))
	current_date = start_date
	days = []
	while current_date < end_date:
		days.append(current_date)
		current_date += delta
	return days

def gen_lname():
	return fake.last_name()

def gen_password():
	return fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

def gen_paragraph():
	return fake.paragraph(nb_sentences=5, variable_nb_sentences=True, ext_word_list=None)

def gen_sentance():
	return fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None)

def pick_user():
	return random.choice(User.objects.all())

def gen_address():
	return fake.address()

def gen_datetime(datetime=None):
	if datetime != None:
		return fake.date_time_between(start_date=datetime, end_date="-18d", tzinfo=None)
	return fake.date_this_year(before_today=True, after_today=False)

def gen_birthdate():
	return fake.date_this_century(before_today=True, after_today=False)

def pick_category(categories=None):
	if categories != None:
		return random.choice(Category.objects.exclude(name=categories.name).all())
	return random.choice(Category.objects.all())

def pick_days():
	day1 = random.choice(Day.objects.all())
	day2 = random.choice(Day.objects.exclude(name=day1.name).all())
	return [day1,day2]

def pick_hours():
	hour1 = random.choice(Hour.objects.all())
	hour2 = random.choice(Hour.objects.exclude(name=hour1.name))
	hour3 = random.choice(Hour.objects.exclude(name=hour1.name).exclude(name=hour2.name))
	return [hour1,hour2,hour3]

def create_patient_users(number):
	'''create x users'''
	users = []
	for i in range(0, number):
		password = gen_password()
		fname = gen_fname()
		lname = gen_lname()
		username = fname.lower() + lname.lower()
		user = User.objects.create_user(username=username, password=password, first_name=fname, last_name=lname, is_patient=True)
		user.save()
		userdict = {'username' : username, 'password' : password}
		users.append(userdict)
	print(users)

def seed_patient_profile():
	for profile in Patient.objects.all():
		profile.categories.add(pick_category())
		profile.bio = gen_sentance()
		profile.birthdate = gen_birthdate()
		profile.gender = random.choice(['M','F'])
		profile.picture = '/media/images/dogpatient.jpg' 
		profile.save()

def create_categories():
	wordlist = ['Family','Trauma', 'Marriage', 'Work', 'Life']
	for word in wordlist:
		cat = Category(name=word)
		cat.save()


def seed_therapist():
	for profile in Therapist.objects.all():
		category1 = pick_category()
		category2 = pick_category(category1)
		profile.categories.add(category1, category2)
		profile.bio = gen_paragraph()
		profile.birthdate = gen_birthdate()
		profile.gender = random.choice(['M','F']) 
		profile.address = gen_address()
		profile.experience = random.randint(1,15)
		profile.languages = random.choice(['English', 'Hebrew', 'Klingon', 'Elvish'])
		profile.picture = '/media/images/catshrink.jpg'
		profile.save()


def create_therapist_users(number):
	'''create x users'''
	users = []
	for i in range(0, number):
		password = gen_password()
		fname = gen_fname()
		lname = gen_lname()
		username = fname.lower() + lname.lower()
		user = User.objects.create_user(username=username, password=password, first_name=fname, last_name=lname, is_patient=False)
		user.save()
		userdict = {'username' : username, 'password' : password}
		users.append(userdict)
	print(users)


def seed_days():
	daycode = 0
	for i in ['Monday','Tuesday','Wednesday','Thursday','Friday']:
		day = Day(name=i, daycode=daycode)
		day.save()
		daycode += 1


def seed_hours():
	for n in [10,11,12,13,14,15,16,17]:
		hour = Hour(name=n)
		hour.save()


def seed_doc_day_times():
	for profile in Therapist.objects.all():
		hours = pick_hours()
		days = pick_days()
		profile.working_hours.add(*hours)
		profile.working_days.add(*days)


def seed_appts():
	appt_list = []
	days = date_list()
	for profile in Therapist.objects.all():
		for day in days:
			working_days = []
			for working_day in profile.working_days.all():
				working_days.append(working_day.daycode)
			if day.weekday() in working_days:
				print('success')
				for hour in profile.working_hours.all():
					print('success2')
					string = f'{day.year}-{day.month}-{day.day} {hour.name}:00:00'
					appt_dt = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
					t_session = TherapySession(datetime=appt_dt, therapist=profile)
					appt_list.append(t_session)
	TherapySession.objects.bulk_create(appt_list)


def seed_new_appts():
	appt_list = []
	days = date_list(TherapySession.objects.last().datetime)
	for profile in Therapist.objects.all():
		for day in days:
			working_days = []
			for working_day in profile.working_days.all():
				working_days.append(working_day.daycode)
			if day.weekday() in working_days:
				print('success')
				for hour in profile.working_hours.all():
					print('success2')
					string = f'{day.year}-{day.month}-{day.day} {hour.name}:00:00'
					appt_dt = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
					t_session = TherapySession(datetime=appt_dt, therapist=profile)
					appt_list.append(t_session)
	TherapySession.objects.bulk_create(appt_list)


if Hour.objects.all().count() == 0:
	seed_hours()

if Day.objects.all().count() == 0:
	seed_days()

if Category.objects.all().count() == 0:
	create_categories()


if Therapist.objects.all().count() == 0:
	create_therapist_users(4)
	seed_therapist()
	seed_doc_day_times()

if Patient.objects.all().count() == 0:
	create_patient_users(4)
	seed_patient_profile()

if TherapySession.objects.all().count() == 0:
	seed_appts()