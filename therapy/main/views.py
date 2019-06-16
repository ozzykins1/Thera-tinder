import pytz, datetime
from django.db.models import Max
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from therapy.middleware.login_exempt import login_exempt
from .models import *
from .forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth import login, authenticate
from datetime import timedelta

def profile_edit(request, id):
	if not request.user.is_patient:
		return redirect('doctor_profile_edit', doc_id=id)
	patient = Patient.objects.filter(id=id).first()
	form = PatientForm(instance=patient)
	form2 = UserForm(instance=patient.user)
	if request.method == "POST":
		form = PatientForm(request.POST, instance=patient)
		form2 = UserForm(request.POST, instance=patient.user)
		if form.is_valid() and form2.is_valid():
			form.save()
			form2.save()
			return redirect('index')
	return render(request, 'profile_edit.html', {'patient' : patient, 'form' : form, 'form2' : form2})

	

def doctor_profile_edit(request, doc_id):
	if request.user.is_patient:
		return redirect('profile_edit')
	therapist = Therapist.objects.filter(id=doc_id).first()
	form = TherapistForm(instance=therapist)
	form2 = UserForm(instance=therapist.user)
	if request.method == "POST":
		form = TherapistForm(request.POST, instance=therapist)
		form2 = UserForm(request.POST, instance=therapist.user)
		if form.is_valid() and form2.is_valid():
			form.save()
			form2.save()
	return render(request, 'doctor_profile_edit.html', {'therapist' : therapist, 'form' : form, 'form2' : form2})

def doctor_profile(request, doc_id):
	therapist = Therapist.objects.filter(id=doc_id).first()
	'''this will have the initial chat space display this as a card'''
	return render(request, 'doctor_profile.html', {'therapist' : therapist})

def doctor_index(request):
	'''this will have the initial chat space'''
	chats = Chat.objects.filter(therapist=request.user.therapist)
	q1 = TherapySession.objects.values('patient').distinct().annotate(x=Max('id'))
	appts = TherapySession.objects.filter(id__in=[i["x"] for i in q1])
	weekly_appts = TherapySession.objects.filter(therapist=request.user.therapist, datetime__gte=(timezone.now() + timedelta(days=7)), patient__isnull=False)
	return render(request, 'doctor_index.html', {'chats' : chats, 'appts' : appts, 'weekly_appts' : weekly_appts })

def index(request):
	if not request.user.is_patient:
		return redirect('doctor_index')
	therapists = Therapist.objects.filter(categories__in=request.user.patient.categories.all()).distinct()
	next_appt = TherapySession.objects.filter(patient=request.user.patient, datetime__gte=timezone.now()).order_by('datetime').first()
	return render(request, 'index.html', {'therapists' : therapists, 'next_appt' : next_appt})

def patient_matched_index(request):
	return render(request, 'patient_matched_index.html')

@login_exempt
def signup(request):
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_patient=True
			user.is_active = False
			user.save()
			'''hashing process here to give link'''
			current_site = get_current_site(request)
			mail_subject = 'Activate your Thera-Tinder account.'
			message = render_to_string('acc_active_email.html', {
				'user': user,
				'domain': current_site.domain,
				'uid':urlsafe_base64_encode(force_bytes(user.pk)),
				'token':account_activation_token.make_token(user),
			})
			to_email = form.cleaned_data.get('email')
			email = EmailMessage(
						mail_subject, message, to=[to_email]
			)
			email.send()

			return HttpResponse('Please confirm your email address to complete the registration') #should redirect to dead end page until user confirms email
	form = CustomUserCreationForm()
	return render(request, 'registration/signup.html', {'form' : form})

@login_exempt
def front(request):
	if request.user.is_authenticated:
		return redirect('index')
	return render(request, 'front.html')

@login_exempt
def about(request):
	return render(request, 'about.html')

def patient_chat(request, therapist_id):
	therapist = Therapist.objects.filter(pk=therapist_id).first()
	chat = Chat.objects.filter(therapist__id=therapist_id).filter(patient__id=request.user.patient.id).first()
	unread_msg_ids = []
	unread_messages = Message.objects.filter(chat=chat,read=False, user=therapist.user)
	for message in unread_messages:
		unread_msg_ids.append(message.id)	
	unread_messages.update(read=True)

	if request.user.is_patient and chat == None:
		chat = Chat(therapist=Therapist.objects.get(pk=therapist_id), patient=request.user.patient)
		chat.save()
	if request.method == 'POST':
		message = Message(chat=chat, content=request.POST.get('content'), user=request.user)
		message.save()
	messages = Message.objects.filter(chat=chat).count()
	return render(request, 'chat.html', {'chat' : chat, 'unread_msg_ids' : unread_msg_ids, 'messages' : messages})


def therapist_chat(request, chat_id):
	chat = Chat.objects.filter(pk=chat_id).first()
	unread_messages = Message.objects.filter(chat=chat,read=False, user=chat.patient.user)
	if chat.therapist != request.user.therapist:
		#flash message "not your chat to see"
		return redirect('index')

	if request.method == 'POST':
		message = Message(chat=chat, content=request.POST.get('content'), user=request.user)
		message.save()
	unread_messages.update(read=True)
	return render(request, 'therapist_chat.html', {'chat' : chat})


def all_therapist_chats(request, therapist_id):
	chats = Chat.objects.filter(therapist__id=therapist_id).all()
	return render(request, 'doc_chats.html', {'chats' : chats})


def all_patient_chats(request, patient_id):
	chats = Chat.objects.filter(patient__id=patient_id).all()
	return render(request, 'doc_chats.html', {'chats' : chats})

@login_exempt
def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
		#flash message saying thanks
		return redirect('index')
	else:
		return HttpResponse('Activation link is invalid!')

def book_session(request, therapist_id):
	therapist = Therapist.objects.filter(pk=therapist_id).first()
	now = timezone.now()
	return render(request, 'book_session.html', {'therapist' : therapist, 'now' : now})

def pick_session(request, therapy_session_id):
	therapy_session = TherapySession.objects.filter(pk=therapy_session_id).first()
	therapy_session.patient = request.user.patient
	therapy_session.save()
	return redirect('index')


@login_exempt
def showimage(request):
    lastimage= Image.objects.last()
    imagefile= lastimage.imagefile
    form= ImageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()

    context= {'imagefile': imagefile,
              'form': form
              }
    return render(request, 'image.html', context)

    
def view_session(request, therapy_session_id):
	appointment = TherapySession.objects.filter(pk=therapy_session_id).first()
	chat = Chat.objects.filter(therapist=request.user.therapist, patient=appointment.patient).first()
	if request.user != appointment.therapist.user:
		return redirect('index')

	if request.method == 'POST':
		form = TherapistSessionLogForm(request.POST)
		if form.is_valid():
			log = form.save(commit=False)
			log.therapysession = appointment
			log.save()
			return redirect('view_session', appointment.id)
	now = timezone.now()
	all_appts = TherapySession.objects.filter(therapist=appointment.therapist, patient=appointment.patient)
	session_logs = []
	for appt in all_appts:
		session_logs.append(SessionLog.objects.filter(therapysession=appt).first())

	form = TherapistSessionLogForm()
	return render(request, 'doc_view_appt.html', {'appointment' : appointment, 'now' : now, 'session_logs' : session_logs, 'form' : form, 'chat' : chat})


def mark_attendance(request, therapy_session_id , attendance):
	therapy_session = TherapySession.objects.filter(pk=therapy_session_id).first()
	if therapy_session == None or attendance not in [1,2] or request.user != therapy_session.therapist.user:
		return redirect('view_session', therapy_session.id)
	if attendance == 1:
		therapy_session.occured = True
	elif attendance == 2:
		therapy_session.occured = False
	therapy_session.save()	
	return redirect('view_session', therapy_session.id)
