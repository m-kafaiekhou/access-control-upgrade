import datetime
import os
import threading
from typing import Any
from django.forms.models import BaseModelForm
import numpy as np
from pytz import timezone

from videostream.views import gen
from .forms import RegistrationForm, LoginForm, PersonalRegistrationForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic, View
from django.contrib.auth.views import auth_login, auth_logout, PasswordResetConfirmView
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import Communication, Department, Operator, Personal, PersonalLog, OperatorLog, DoorOpenLog
from django.http import HttpResponse, JsonResponse
from http import HTTPStatus
from datetime import time, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from jdatetime import datetime as jdatetime
import jdatetime as jdt
import pandas as pd
from .utils import find_usb_port

from pydub import AudioSegment
from pydub.playback import play
import serial
import pickle
import adafruit_fingerprint
from time import sleep
import cv2
from deepface import DeepFace
import queue
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from PIL import Image

try:
    frame_q = queue.Queue()
    cap = cv2.VideoCapture(0)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except:
    print("exception in init views")
    
desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
path_finger_pkl = os.path.join(desktop_path, r'access_control\node\DataSet\FingerPrint\personal_finger.pkl')
path_image = os.path.join(desktop_path, r'access_control\node\DataSet\Image')
mp3_directory = os.path.join(desktop_path, r'access_control\node\MP3')

mp3_files = [
    'Empty.mp3',      #[0]
    'Facedetect.mp3', #[1]
    'closedoor.mp3',  #[2]
    'fingerprint.mp3',#[3]
    'nopermit.mp3',   #[4]
    'opendoor.mp3',   #[5]
    'wait.mp3',       #[6]
    'log.mp3',        #[7]
    'hse.mp3',        #[8]
    'registering.mp3',#[9]
    'sendtoacq.mp3',  #[10]
    'registeryend.mp3',#[11]
    'Repeat.mp3'      #[12]
]

def cv_thread(frameq):
    while True:
        _, frame = cap.read()

        if _:
            while frame_q.qsize() > 1:
                frame_q.get()
            frame_q.put(frame)

threading.Thread(target=cv_thread, args=(frame_q, )).start()


def play_mp3_track(track_idx):
        pass
        # print(os.path.join(mp3_directory, "test.mp3"))
        # song = AudioSegment.from_mp3(os.path.join(mp3_directory, "test.mp3"))
        # play(song)


def detect_face(frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if isinstance(faces, tuple):
                return  False
            else:
                return  True
        except Exception as e:
                print('Detect Face Error is :', e)


def enroll_finger(pid, finger):
    global status
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            status = "Place finger on sensor..."
        else:
            status = "Place same finger again..."

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                status = "Image taken"
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                status = "Imaging error"
                return (False, 'اثر انگشت ثبت نشد', )
            else:
                status = "Other error"
                return (False, 'اثر انگشت ثبت نشد', )

        status = "Templating..."
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            status = "Templated"
        else:
            return (False, 'اثر انگشت ثبت نشد', )

        if fingerimg == 1:
            status = "Remove finger"
            sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    status = "Creating model..."
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        status = "Created"
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            status = "Prints did not match"
        else:
            status = "Other error"
        return (False, 'اثر انگشت ثبت نشد', )
    
    template = finger.get_fpdata()

    person_dict = {'pid': [pid],
                   'template': [template],
                   }
    
    person_df = pd.DataFrame(person_dict)   
    
    with open(path_finger_pkl, 'rb') as f:
            persons = pickle.load(f)
    if person_dict['pid'] not in persons['pid'].values:
            persons=pd.concat([persons, person_df], ignore_index=True)
            with open(path_finger_pkl, 'wb') as file:
                    pickle.dump(persons, file)
            status = "personel added succefully!"

    else:
            status = 'Person Id is exists'
            return (True, 'اثر انگشت قبلا ثبت شده', )

    
                
    return (True, 'اثر انگشت با موفقیت ثبت شد', )

def reg_face(pid):
    try:
        frame = frame_q.queue[0]
    except IndexError:
        return (False, 'در گرفتن تصویر مشکلی پیش امده')
        
    isFace = detect_face(frame) 
    
    if isFace:
        try:
            for filename in os.listdir(path_image):
                if filename.split('.')[0] == str(pid):
                    return (True, 'تصویر با این شماره پرسنلی وجود دارد', )
                # if filename.endswith(".pkl"):
                #     os.remove(os.path.join(path_image, filename))
                
            cv2.imwrite(os.path.join(path_image, f'{pid}.jpg'), frame)

            # new_rep_one = DeepFace.find(
            #     img_path=frame,
            #     db_path=path_image,
            #     model_name="SFace",
            #     detector_backend="ssd",
            #     enforce_detection=True
            #     )
            # new_rep_two = DeepFace.find(
            #     img_path=frame,
            #     db_path=path_image,
            #     model_name="Dlib",
            #     detector_backend="ssd",
            #     enforce_detection=True,
            #     )
        except:
            return (False, 'ثبت تصویر با مشکل مواجه شد', )
        else:
            
            return (True, 'تصویر با موفقیت ثبت گردید', )
    else:
        return (False, 'در تصویر چهره وجود ندارد', )
        
@gzip.gzip_page
def livestream_view(request):
    try:
        response = StreamingHttpResponse(gen(frame_q), content_type="multipart/x-mixed-replace;boundary=frame")
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        raise e
    

class RegistrationView(UserPassesTestMixin, generic.CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "registration/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        return context
    
    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        data = form_kwargs.get('data')
        print(data)
        
        if data is not None:
            data = data.copy()
            job = form_kwargs.get('data').get('job')
            year = form_kwargs.get('data').get('year')
            month = form_kwargs.get('data').get('month')
            day = form_kwargs.get('data').get('day')
            expire = f'{year}-{month}-{day}'

            data['job'] = job
            data['expire'] = expire

            form_kwargs.update(
                {'data': data}
                )

        return form_kwargs

    def test_func(self):
        return self.request.user and self.request.user.is_staff


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = "registration/login.html"
    success_url = reverse_lazy("cctv:cctv")

    def form_valid(self, form):
        user = authenticate(self.request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user and not user.is_deleted:
            date_now = jdt.date.fromgregorian(date=datetime.datetime.now().date())
            if user.expire < date_now:
                return HttpResponse("حساب کاربر منقضی شده است")
            
            now = datetime.datetime.now()

            date_now = f'{now.year}-{now.month}-{now.day}'

            tehran_timezone = timezone('Asia/Tehran')
            tehran_time = now.astimezone(tehran_timezone).time()
            
            time_now = time(hour=tehran_time.hour, minute=tehran_time.minute, second=tehran_time.second)

            log_kwargs = {
                "operator": user,
                "date_in": date_now,
                "time_in": time_now,
                "state": "entry"
            }

            OperatorLog.objects.create(**log_kwargs)

            auth_login(self.request, user)
            return redirect(self.get_success_url())
        else:
            messages.info(self.request, "Invalid username or password", "info")
            return redirect(reverse_lazy('accounts:login'))


class LogoutView(LoginRequiredMixin, View):
    success_url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        user = request.user

        auth_logout(request)

        log = OperatorLog.objects.filter(operator=user).last()

        now = datetime.datetime.now()

        date_now = f'{now.year}-{now.month}-{now.day}'

        tehran_timezone = timezone('Asia/Tehran')
        tehran_time = now.astimezone(tehran_timezone).time()
        
        time_now = time(hour=tehran_time.hour, minute=tehran_time.minute, second=tehran_time.second)

        log.date_out = date_now
        log.time_out = time_now
        log.state = 'exit'

        log.save()

        return redirect(self.success_url)
    

class IndexView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class RegisterPersonel(UserPassesTestMixin, View):

    def get(self, request, *args, **kwargs):
        departments = Department.objects.all()
        return render(request, 'registration/register_personal.html', context={'departments': departments})

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()

        y1 = data.get('year1')
        m1 = data.get('month1')
        d1 = data.get('day1')

        y2 = data.get('year2')
        m2 = data.get('month2')
        d2 = data.get('day2')

        h1 = int(data.get('hour1'))
        min1 = int(data.get('minute1'))
        s1 = int(data.get('second1'))

        h2 = int(data.get('hour2'))
        min2 = int(data.get('minute2'))
        s2 = int(data.get('second2'))

        permit_date_start = f'{y1}-{m1}-{d1}'
        permit_date_stop = f'{y2}-{m2}-{d2}'

        permit_time_start = time(hour=h1, minute=min1, second=s1)
        permit_time_stop = time(hour=h2, minute=min2, second=s2)
    
        shift = {
            "shift_A": data.get('shift_A'),
            "shift_B": data.get('shift_B'),
            "shift_C": data.get('shift_C')
        }

        permit = {
            "server_room_permit": data.get("server_room_permit")=="True",
            "control_room_permit": data.get("control_room_permit")=="True",
            "ups_room_permit": data.get("ups_room_permit")=="True",
            "operation_permit": data.get("operation_permit")=="True",
            "supervision_permit": data.get("supervision_permit")=="True",
            "service_permit": data.get("service_permit")=="True",
        }

        _type = ''.join(data.getlist('type'))

        form_kwargs = {
                "name": data.get('name'),
                "family": data.get('family'),
                "PID": data.get('PID'),
                "phone": data.get('phone'),
                "department": data.get('department'),
                "permit_date_start": permit_date_start,
                "permit_date_stop": permit_date_stop,
                "permit_time_start": permit_time_start,
                "permit_time_stop": permit_time_stop,
                "position": data.get('position'),
                "shift": shift,
                "type": _type,
                "permit": permit,
                "operator": request.user.id
             }
        
        form = PersonalRegistrationForm(form_kwargs)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, "پرسنل با موفقیت اضافه شد")
            return redirect(request.path)
        
        messages.warning(request, "بعد از بررسی اطلاعات فرم دوباره تلاش کنید")
        return redirect(request.path)
    
    def test_func(self):
        return self.request.user and self.request.user.job != "بهره بردار"


class CommunicationView(View):
    def post(self, request, *args, **kwargs):
        action = kwargs.get('action')
        pid = request.POST.get("PID")
        print(request.POST)
        
        

        if action == "finger":
            try:
                uart = serial.Serial(find_usb_port('Prolific USB-to-Serial Comm Port'), baudrate=57600, timeout=10)
                finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
                print("333 ln")
                finger_success, msg = enroll_finger(pid, finger)
                print("335 ln")

            except Exception as e:
                print("338 ln", e)
                return JsonResponse({"msg": "اثر انگشت ثبت نشد"}, safe=False , status=HTTPStatus.BAD_REQUEST)
            
            finally:
                if 'uart' in locals() and uart is not None:
                    uart.close()

            if finger_success:
                return JsonResponse({'msg': msg}, safe=False , status=HTTPStatus.CREATED)
            else:
                print("345 ln")

                return JsonResponse({'msg': msg}, safe=False , status=HTTPStatus.BAD_REQUEST)

        elif action == "image":
            face_success, msg = reg_face(pid)
            if face_success:
                return JsonResponse({'msg': msg}, safe=False, status=HTTPStatus.CREATED)
            else:
                return JsonResponse({'msg': msg}, safe=False, status=HTTPStatus.BAD_REQUEST)
        else:
            return JsonResponse({"msg": "Invalid action"}, safe=False , status=HTTPStatus.BAD_REQUEST)
        

class GetLastRecognized(View):
    def get(self, request):
        obj = PersonalLog.objects.order_by("-date_in", "-time_in").first()

        if obj is None:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)
        person = obj.personal 

        permit = []

        _p = person.permit

        if _p.get('server_room_permit'):
            permit.append("سرور")
        if _p.get('control_room_permit'):
            permit.append("کنترل")
        if _p.get('ups_room_permit'):
            permit.append("UPS")
        if _p.get('operation_permit'):
            permit.append("اجرایی")
        if _p.get('supervision_permit'):
            permit.append("نظارتی")
        if _p.get('service_permit'):
            permit.append("خدماتی")

        permits = ",".join(permit)

        data = {
            'name': person.name,
            'family': person.family,
            'fullname': f'{person.name} {person.family}',
            'phone': person.phone,
            'permit': permits,
            'expire_date': str(person.permit_date_stop)
        }
        
        return JsonResponse(data)


class PasswordChangeView(UserPassesTestMixin, View):
    form_class = PasswordChangeForm

    def get(self, request):
        return render(request, 'registration/password_change.html')

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            return redirect(reverse_lazy('accounts:login'))
        
        errors = form.errors.as_data()
        # You can now access the specific errors for each field
        for field, error_list in errors.items():
            error_message = error_list[0].message 
            print(error_message)
        
        return redirect(reverse_lazy('accounts:password-change'))
    
    def test_func(self):
        return self.request.user and self.request.user.is_staff


class EditPersonalView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        name = request.GET.get('name')
        family = request.GET.get('family')
        pid = request.GET.get('pid')

        query = Q() 
        if name:
            query &= Q(name__icontains=name)  
        if family:
            query &= Q(family__icontains=family)  
        if pid:
            query &= Q(PID=pid)  
        
        qs = Personal.objects.filter(query).order_by("-date_joined")

        first_personal = qs.first()

        departments = Department.objects.all()

        context = {
            'personals': qs,
            'fp': first_personal,
            'departments': departments
        }

        return render(request, 'registration/edit_personal.html', context=context)
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        permit_date_stop = data.get('permit_date_stop')
        permit_time_stop = data.get('permit_time_stop')
    
        shift = {
            "shift_A": data.get('shift_A'),
            "shift_B": data.get('shift_B'),
            "shift_C": data.get('shift_C')
        }

        permit = {
            "server_room_permit": data.get("server_room_permit")=="True",
            "control_room_permit": data.get("control_room_permit")=="True",
            "ups_room_permit": data.get("ups_room_permit")=="True",
            "operation_permit": data.get("operation_permit")=="True",
            "supervision_permit": data.get("supervision_permit")=="True",
            "service_permit": data.get("service_permit")=="True",
        }

        pid = data.get('pid')

        personal = get_object_or_404(Personal, PID=pid)

        if request.user.job == "بهره بردار":
            certify = True
        else:
            certify = personal.certify

        form_kwargs = {
                "name": data.get('name'),
                "family": data.get('family'),
                "phone": data.get('phone'),
                "department_id": int(data.get('department')),
                "permit_date_stop": permit_date_stop,
                "permit_time_stop": permit_time_stop,
                "position": data.get('position'),
                "shift": shift,
                "permit": permit,
                "operator": request.user,
                "certify": certify
             }
        

        for attr, value in form_kwargs.items():
            setattr(personal, attr, value)

        if personal.first_editor is None:
            personal.first_editor = request.user
        
        elif personal.second_editor is None:
            personal.second_editor = request.user

        personal.save()

        return redirect(reverse_lazy('accounts:edit-personal'))
    

class DeletePersonalView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pid = request.POST.get('pid')

        personel_delete = False
        finger_delete = False
        face_delete = False

        try:    
            with open(path_finger_pkl, 'rb') as f:
                persons = pickle.load(f)
        
            if pid in persons['pid'].values:
                persons = persons[persons['pid'] != pid]
                with open(path_finger_pkl, 'wb') as file:
                    pickle.dump(persons, file)
            else:
                finger_delete = True
        except Exception as e:
            print(e)
            pass
        else:
            finger_delete = True

        
        try:
            img_path = os.path.join(path_image, f'{pid}.jpg')
            if not os.path.isfile(img_path):
                face_delete = True
            os.remove(img_path)
            face_delete = True
            frame = np.zeros(shape=[100,100,3], dtype=np.uint8)

            DeepFace.find(
                    img_path=frame,
                    db_path=path_image,
                    model_name="GhostFaceNet",
                    detector_backend="ssd",
                    enforce_detection=False
                    )
        except Exception as e: 
            print(e)
            pass
        else:
            face_delete = True
        
        try:
            print(pid)
            personal = get_object_or_404(Personal, PID=pid)
            personal.delete()
        except Exception as e:
            print(e)
            personel_delete = False
        else:
            personel_delete = True
        
        redirect_flag = True

        if face_delete and finger_delete and personel_delete:
            msg = 'پرسنل با موفقیت حذف گردید'
        elif personel_delete and finger_delete == False and face_delete == False:
            msg = "پرسنل پاک شد اما اثر انگشت و چهره پاک نشد"
        elif personel_delete and finger_delete and face_delete == False:
            msg = "پرسنل پاک شد اما چهره پاک نشد"
        elif personel_delete and finger_delete == False and face_delete:
            msg = "پرسنل پاک شد اما اثر انگشت پاک نشد"
        else:
            redirect_flag = False
            msg = "پرسنل پاک نشد"
        
        status_code = HTTPStatus.OK if redirect_flag else HTTPStatus.BAD_REQUEST

        return JsonResponse(data={'redirect': reverse_lazy('accounts:edit-personal'), 'msg': msg}, status=status_code)


class PersonalEnterLogView(View):
    def get(self, request, *args, **kwargs):
        status = HTTPStatus.BAD_REQUEST
        
        pid = request.GET.get('pid')

        personal = get_object_or_404(Personal, PID=pid)

        if not personal.certify or not personal.permit.get("server_room_permit"):
            return HttpResponse('no permit or not certified', status=status)
        

        lastlog = PersonalLog.objects.filter(personal=personal).last()

        now = datetime.datetime.now()

        _date_now = jdt.date.fromgregorian(date=now.date())

        # if pid == 'admin' and lastlog and lastlog.date_in == _date_now and lastlog.time_in.minute == now.minute:
        #     return HttpResponse('log already exists', status=status)

        if not personal.permit_date_start < _date_now < personal.permit_date_stop:
            return HttpResponse('permit expired', status=status)

        status = HTTPStatus.OK

        date_now = f'{now.year}-{now.month}-{now.day}'

        tehran_timezone = timezone('Asia/Tehran')
        tehran_time = now.astimezone(tehran_timezone).time()
        
        time_now = time(hour=tehran_time.hour, minute=tehran_time.minute, second=tehran_time.second)

        log_kwargs = {
            "personal": personal,
            "date_in": date_now,
            "time_in": time_now,
            "state": "entry"
        }

        PersonalLog.objects.create(**log_kwargs)

        return HttpResponse('Log Created Successfully', status=status)


class PersonalExitLogView(View):
    def get(self, request, *args, **kwargs):
        status = HTTPStatus.BAD_REQUEST
        pid = request.GET.get('pid')

        personal = get_object_or_404(Personal, PID=pid)

        if not personal.certify or not personal.permit.get("server_room_permit"):
            return HttpResponse('no permit or not certified', status=status)
        

        lastlog = PersonalLog.objects.filter(personal=personal).last()

        now = datetime.datetime.now()

        _date_now = jdt.date.fromgregorian(date=now.date())

        if not personal.permit_date_start < _date_now < personal.permit_date_stop:
            return HttpResponse('permit expired', status=status)

        status = HTTPStatus.OK

        date_now = f'{now.year}-{now.month}-{now.day}'

        tehran_timezone = timezone('Asia/Tehran')
        tehran_time = now.astimezone(tehran_timezone).time()
        
        time_now = time(hour=tehran_time.hour, minute=tehran_time.minute, second=tehran_time.second)

        if lastlog and not lastlog.date_out and not lastlog.time_out:
            lastlog.time_out = time_now
            lastlog.date_out = date_now
            lastlog.state = 'exit'
            lastlog.save()

            return HttpResponse('Log Created Successfully', status=status)

        elif not lastlog:
            PersonalLog.objects.create(
                personal=personal,
                time_out = time_now,
                date_out=date_now,
                state='exit'
            )
            return HttpResponse('Entry Log Does not exists', status=status)
        
        elif lastlog.date_out or lastlog.time_out:
            PersonalLog.objects.create(
                personal=personal,
                time_out = time_now,
                date_out=date_now,
                state='exit'
            )
            return HttpResponse('Log already has exit date or time', status=status)
        
        return HttpResponse('something went wrong', status=HTTPStatus.EXPECTATION_FAILED)


class PersonalLogReportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        name = request.GET.get('name')
        family = request.GET.get('family')
        pid = request.GET.get('pid')

        y1 = request.GET.get('year1')
        m1 = request.GET.get('month1')
        d1 = request.GET.get('day1')

        y2 = request.GET.get('year2')
        m2 = request.GET.get('month2')
        d2 = request.GET.get('day2')
        if y1 and m1 and d1:
            date_from_str = f'{y1}-{m1}-{d1}'
        else:
            date_from_str = None

        if y2 and m2 and d2:
            date_till_str = f'{y2}-{m2}-{d2}'
        else:
            date_till_str = None

        try:
            h1 = int(request.GET.get('hour1'))
            min1 = int(request.GET.get('minute1'))
            s1 = int(request.GET.get('second1'))

            time_from = time(hour=h1, minute=min1, second=s1)

            
        except Exception as e:
            print(e)
            time_from = None
        
        try:
            h2 = int(request.GET.get('hour2'))
            min2 = int(request.GET.get('minute2'))
            s2 = int(request.GET.get('second2'))

            time_till = time(hour=h2, minute=min2, second=s2)

        except Exception as e:
            print(e)
            time_till = None

        
        query = Q() 
        if name:
            query &= Q(personal__name__icontains=name)  
        if family:
            query &= Q(personal__family__icontains=family)  
        if pid:
            query &= Q(personal__PID=pid)
        if date_from_str:
            date_from = jdatetime.strptime(date_from_str, '%Y-%m-%d')
            query &= Q(date_in__gte=date_from)  
        if date_till_str:
            date_till = jdatetime.strptime(date_till_str, '%Y-%m-%d')
            query &= Q(date_in__lte=date_till)
        if time_from:
            query &= Q(time_in__gte=time_from)  
        if time_till:
            query &= Q(time_in__lte=time_till)
        
        qs = PersonalLog.objects.select_related('personal').filter(query).order_by("-date_in", "-time_in")

        context = {
            'logs': qs
        }

        return render(request, 'registration/personal_log_report.html', context=context)


class DownloadPersonalLogView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(previous_url)
            get_params = parse_qs(parsed_url.query)
        
        print(get_params)
        name = get_params.get('name')
        family = get_params.get('family')
        pid = get_params.get('pid')

        y1 = get_params.get('year1')
        m1 = get_params.get('month1')
        d1 = get_params.get('day1')

        y2 = get_params.get('year2')
        m2 = get_params.get('month2')
        d2 = get_params.get('day2')

        try:
            h1 = int(get_params.get('hour1')[0])
            min1 = int(get_params.get('minute1')[0])
            s1 = int(get_params.get('second1')[0])

            time_from = time(hour=h1, minute=min1, second=s1)
        except Exception as e:
            time_from = None

        try:
            h2 = int(get_params.get('hour2')[0])
            min2 = int(get_params.get('minute2')[0])
            s2 = int(get_params.get('second2')[0])

            time_till = time(hour=h2, minute=min2, second=s2)
        except Exception as e:
            time_till = None

        if y1 and m1 and d1:
            date_from_str = f'{y1[0]}-{m1[0]}-{d1[0]}'
        else:
            date_from_str = None

        if y2 and m2 and d2:
            date_till_str = f'{y2[0]}-{m2[0]}-{d2[0]}'
        else:
            date_till_str = None

        query = Q() 
        if name:
            query &= Q(personal__name__icontains=name[0])  
        if family:
            query &= Q(personal__family__icontains=family[0])  
        if pid:
            query &= Q(personal__PID=pid[0])
        if date_from_str:
            date_from = jdatetime.strptime(date_from_str, '%Y-%m-%d')
            query &= Q(date_in__gte=date_from)  
        if date_till_str:
            date_till = jdatetime.strptime(date_till_str, '%Y-%m-%d')
            query &= Q(date_in__lte=date_till)
        if time_from:
            query &= Q(time_in__gte=time_from)  
        if time_till:
            query &= Q(time_in__lte=time_till)
        
        qs = PersonalLog.objects.select_related('personal').filter(query).order_by("-date_in", "-time_in").values_list(
            'personal__name',
            'personal__family',
            'personal__department__name',
            'personal__PID',
            'personal__shift',
            'personal__phone',
            'personal__permit',
            'personal__position',
            'date_in',
            'date_out',
            'time_in',
            'time_out'
        )

        print(qs)
        df = pd.DataFrame(qs, columns=[
                            'Name',
                            'Family',
                            'Department Name',
                            'PID',
                            'Shift',
                            'Phone',
                            'Permit',
                            'Position',
                            'Date In',
                            'Date Out',
                            'Time In',
                            'Time Out'
                        ])
        print(df)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="PersonelReport.xlsx"'                                        
        df.to_excel(response)

        return response
    

class OperatorLogReportView(UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        name = request.GET.get('name')
        family = request.GET.get('family')
        pid = request.GET.get('pid')

        y1 = request.GET.get('year1')
        m1 = request.GET.get('month1')
        d1 = request.GET.get('day1')

        y2 = request.GET.get('year2')
        m2 = request.GET.get('month2')
        d2 = request.GET.get('day2')
        if y1 and m1 and d1:
            date_from_str = f'{y1}-{m1}-{d1}'
        else:
            date_from_str = None

        if y2 and m2 and d2:
            date_till_str = f'{y2}-{m2}-{d2}'
        else:
            date_till_str = None

        try:
            h1 = int(request.GET.get('hour1'))
            min1 = int(request.GET.get('minute1'))
            s1 = int(request.GET.get('second1'))

            time_from = time(hour=h1, minute=min1, second=s1)

            
        except Exception as e:
            print(e)
            time_from = None
        
        try:
            h2 = int(request.GET.get('hour2'))
            min2 = int(request.GET.get('minute2'))
            s2 = int(request.GET.get('second2'))

            time_till = time(hour=h2, minute=min2, second=s2)

        except Exception as e:
            print(e)
            time_till = None

        
        query = Q() 
        if name:
            query &= Q(operator__name__icontains=name)  
        if family:
            query &= Q(operator__family__icontains=family)  
        if pid:
            query &= Q(operator__PID=pid)
        if date_from_str:
            date_from = jdatetime.strptime(date_from_str, '%Y-%m-%d')
            query &= Q(date_in__gte=date_from)  
        if date_till_str:
            date_till = jdatetime.strptime(date_till_str, '%Y-%m-%d')
            query &= Q(date_in__lte=date_till)
        if time_from:
            query &= Q(time_in__gte=time_from)  
        if time_till:
            query &= Q(time_in__lte=time_till)
        
        qs = OperatorLog.objects.select_related('operator').filter(query).order_by("-date_in", "-time_in")

        context = {
            'logs': qs
        }

        return render(request, 'registration/operator_log_report.html', context=context)

    def test_func(self):
        return self.request.user and self.request.user.is_staff
    

class DownloadOperatorLogView(UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(previous_url)
            get_params = parse_qs(parsed_url.query)
        

        name = get_params.get('name')
        family = get_params.get('family')
        pid = get_params.get('pid')

        y1 = get_params.get('year1')
        m1 = get_params.get('month1')
        d1 = get_params.get('day1')

        y2 = get_params.get('year2')
        m2 = get_params.get('month2')
        d2 = get_params.get('day2')

        try:
            h1 = int(get_params.get('hour1')[0])
            min1 = int(get_params.get('minute1')[0])
            s1 = int(get_params.get('second1')[0])

            time_from = time(hour=h1, minute=min1, second=s1)
        except Exception as e:
            time_from = None

        try:
            h2 = int(get_params.get('hour2')[0])
            min2 = int(get_params.get('minute2')[0])
            s2 = int(get_params.get('second2')[0])

            time_till = time(hour=h2, minute=min2, second=s2)
        except Exception as e:
            time_till = None

        if y1 and m1 and d1:
            date_from_str = f'{y1[0]}-{m1[0]}-{d1[0]}'
        else:
            date_from_str = None

        if y2 and m2 and d2:
            date_till_str = f'{y2[0]}-{m2[0]}-{d2[0]}'
        else:
            date_till_str = None

        query = Q() 
        if name:
            query &= Q(operator__name__icontains=name[0])  
        if family:
            query &= Q(operator__family__icontains=family[0])  
        if pid:
            query &= Q(operator__PID=pid[0])
        if date_from_str:
            date_from = jdatetime.strptime(date_from_str, '%Y-%m-%d')
            query &= Q(date_in__gte=date_from)  
        if date_till_str:
            date_till = jdatetime.strptime(date_till_str, '%Y-%m-%d')
            query &= Q(date_in__lte=date_till)
        if time_from:
            query &= Q(time_in__gte=time_from)  
        if time_till:
            query &= Q(time_in__lte=time_till)
        
        qs = OperatorLog.objects.select_related('operator').filter(query).values_list(
            'operator__name',
            'operator__family',
            'operator__NID',
            'operator__PID',
            'operator__phone',
            'operator__department__name',
            'operator__job',
            'date_in',
            'date_out',
            'time_in',
            'time_out'
        )

        df = pd.DataFrame(qs, columns=[
                            'Name',
                            'Family',
                            "NID",
                            'PID',
                            'Phone',
                            'Department',
                            'Job',
                            'Date In',
                            'Date Out',
                            'Time In',
                            'Time Out'
                        ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="OperatorReport.xlsx"'                                        
        df.to_excel(response)

        return response
    
    def test_func(self):
        return self.request.user and self.request.user.is_staff
    

class EditOperatorView(UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        name = request.GET.get('name')
        family = request.GET.get('family')
        pid = request.GET.get('pid')

        query = Q() 
        if name:
            query &= Q(name__icontains=name)  
        if family:
            query &= Q(family__icontains=family)  
        if pid:
            query &= Q(PID=pid)  
        
        qs = Operator.objects.filter(query).order_by("-date_joined")

        first_operator = qs.first()

        departments = Department.objects.all()

        context = {
            'operators': qs,
            'fo': first_operator,
            'departments': departments
        }

        return render(request, 'registration/edit_operator.html', context=context)
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        expire = data.get('expire')
    
        pid = data.get('pid')

        operator = get_object_or_404(Operator, PID=pid)

        form_kwargs = {
                "name": data.get('name'),
                "family": data.get('family'),
                "phone": data.get('phone'),
                "department_id": int(data.get('department')),
                "job": data.get('job'),
                "expire": expire
             }
        

        for attr, value in form_kwargs.items():
            setattr(operator, attr, value)

        operator.save()

        return redirect(reverse_lazy('accounts:edit-operator'))
    
    def test_func(self):
        return self.request.user and self.request.user.is_staff
    

class DeleteOperatorView(UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        pid = request.POST.get('pid')
        operator = get_object_or_404(Operator, PID=pid)
        operator.is_deleted = True

        operator.save()
        return JsonResponse(data={'redirect': reverse_lazy('accounts:edit-operator')})

    def test_func(self):
        return self.request.user and self.request.user.is_staff
    

class DoorComView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        door = request.POST.get('door', False)
        print(door)
        com = Communication.objects.last()
        print(com)
        com.open_door = door == "true"
        com.save()

        if door == "true":
            operator = request.user
            dt_now = jdt.datetime.now()

            DoorOpenLog.objects.create(operator=operator, dt=dt_now)

        return HttpResponse("success")
    

class TotalComView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        total = request.POST.get('total', False)

        com = Communication.objects.last()
        com.total_enable = total == "true"
        com.save()

        return HttpResponse("success")
    

class GetAlarmView(View):
    def get(self, request, *args, **kwargs):
        com = Communication.objects.last()

        alarm1 = com.alarm1
        alarm2 = com.alarm2

        data = {
            "alarm1": alarm1,
            "alarm2": alarm2
        }
        
        return JsonResponse(data)

class DeleteFaceView(View):
    def post(self, request, *args, **kwargs):
        try:
            pid = request.POST.get('pid')
            
            img_path = os.path.join(path_image, f'{pid}.jpg')
            if not os.path.isfile(img_path):
                return JsonResponse({"msg": "تصویر چهره وجود ندارد"}, status=HTTPStatus.OK)
            os.remove(img_path)
            deleted = True
            frame = np.zeros(shape=[100,100,3], dtype=np.uint8)

            DeepFace.find(
                    img_path=frame,
                    db_path=path_image,
                    model_name="SFace",
                    detector_backend="ssd",
                    enforce_detection=False
                    )
            DeepFace.find(
                img_path=frame,
                db_path=path_image,
                model_name="Dlib",
                detector_backend="ssd",
                enforce_detection=True,
                )
        except Exception as e: 
            if deleted:
                return JsonResponse({"msg":"تصویر چهره با موفقیت پاک شد"}, status=HTTPStatus.OK)

            return JsonResponse({"msg": "تصویر چهره پاک نشد"}, status=HTTPStatus.BAD_REQUEST)
        else:
            return JsonResponse({"msg": "تصویر چهره با موفقیت پاک شد"}, status=HTTPStatus.OK)
        

class DeleteFingerView(View):
    def post(self, request, *args, **kwargs):
        try:
            pid = request.POST.get('pid')
            
            with open(path_finger_pkl, 'rb') as f:
                persons = pickle.load(f)
        
            if pid in persons['pid'].values:
                persons = persons[persons['pid'] != pid]
                with open(path_finger_pkl, 'wb') as file:
                    pickle.dump(persons, file)
            else:
                return JsonResponse({"msg": "اثر انگشت وجود ندارد"}, status=HTTPStatus.OK)
        except:
            return JsonResponse({"msg": "اثر انگشت پاک نشد"}, status=HTTPStatus.BAD_REQUEST)
        else:
            return JsonResponse({"msg": "اثر انگشت با موفقیت پاک شد"}, status=HTTPStatus.OK)



class ShowPersonalImageView(View):
    def post(self, request, *args, **kwargs):
        try:
            pid = request.POST.get('pid')
            
            _path = os.path.join(path_image, f'{pid}.jpg')
            
            if os.path.isfile(_path):  
                img = Image.open(_path)
                img.show()
                return JsonResponse({"msg": "تصویر نمایش داده شد"}, status=HTTPStatus.OK)
                
            else:
                return JsonResponse({"msg": "برای پرسنل تصویری وجود ندارد"}, status=HTTPStatus.BAD_REQUEST)
                
        except:
            return JsonResponse({"msg": "مشکلی در نمایش تصویر بوجود امد"}, status=HTTPStatus.BAD_REQUEST)
        
        
class ShowPersonalFingerView(View):
    def post(self, request, *args, **kwargs):
        try:
            pid = request.POST.get('pid')
            
            with open(path_finger_pkl, 'rb') as f:
                persons = pickle.load(f)
        
            if pid in persons['pid'].values:
                return JsonResponse({"msg": "اثرانگشت برای پرسنل ثبت شده است"}, status=HTTPStatus.OK)
                
            else:
                return JsonResponse({"msg": "برای پرسنل اثرانگشت وجود ندارد"}, status=HTTPStatus.BAD_REQUEST)
                
        except:
            return JsonResponse({"msg": "مشکلی در بررسی اثر انگشت بوجود امد"}, status=HTTPStatus.BAD_REQUEST)
        