# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from json import JSONEncoder
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from web.models import Token, User, Expence, Income, Passwordresetcodes
from datetime import datetime
from django.contrib.auth.hashers import make_password
from postmark import PMMail
from .utils import grecaptcha_verify, get_client_ip
from django.utils.crypto import get_random_string
import string
import time
from django.db.models import Sum, Count

# Create your views here.

# create random string for Toekn
random_str = lambda N: ''.join(
    random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

def register(request):
    if request.POST.has_key(
            'requestcode'):  # form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        # is this spam? check reCaptcha
        if grecaptcha_verify(request):  # captcha was not correct
            context = {
                'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'}  # TODO: forgot password
            return render(request, 'register.html', context)

        # duplicate email
        if User.objects.filter(email=request.POST['email']).exists():
            context = {
                'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
        # if user does not exists
        if not User.objects.filter(username=request.POST['username']).exists():
            code = get_random_string(length=32)
            now = datetime.now()
            email = request.POST['email']
            password = make_password(request.POST['password'])
            username = request.POST['username']
            temporarycode = Passwordresetcodes(
                email=email, time=now, code=code, username=username, password=password)
            temporarycode.save()
            #message = PMMail(api_key=settings.POSTMARK_API_TOKEN,
            #                 subject="فعالسازی اکانت بستون",
            #                 sender="jadi@jadi.net",
            #                 to=email,
            #                 text_body=" برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: {}?code={}".format(
            #                     request.build_absolute_uri('/accounts/register/'), code),
            #                 tag="account request")
            #message.send()
            message = 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'
            message = 'قدیم ها ایمیل فعال سازی می فرستادیم ولی الان شرکتش ما رو تحریم کرده (: پس راحت و بی دردسر'
            body = " برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: <a href=\"{}?code={}\">لینک رو به رو</a> ".format(request.build_absolute_uri('/accounts/register/'), code)
            message = message + body
            context = {
                'message': message }
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
    elif request.GET.has_key('code'):  # user clicked on code
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(
                code=code).exists():  # if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password,
                                          email=new_temp_user.email)
            this_token = get_random_string(length=48)
            token = Token.objects.create(user=newuser, token=this_token)
            # delete the temporary activation code from db
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {
                'message': 'اکانت شما ساخته شد. توکن شما {} است. آن را ذخیره کنید چون دیگر نمایش داده نخواهد شد! جدی!'.format(
                    this_token)}
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'register.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)



@csrf_exempt
def submit_expense(request):
    """user submit an expense"""
    if 'date' not in request.POST:
        now = datetime.now()
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    Expence.objects.create(user = this_user, amount = request.POST['amount'], 
            text = request.POST['text'], date = now)
    print "Expence enterd"
    print request.POST

    return JsonResponse({
        'status': 'ok',
    }, encoder=JSONEncoder)

@csrf_exempt
def submit_income(request):
    """user submit an income"""
    if 'date' not in request.POST:
        now = datetime.now()
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token=this_token).get()
    Income.objects.create(user=this_user, amount=request.POST['amount'],
                text=request.POST['text'], date=now)
    
    print("Income entered")
    print(request.POST)
    return JsonResponse({
            'status': 'ok',
        }, encoder=JSONEncoder)

def index(request):
    context = {}
    return render(request, 'index.html', context)

@csrf_exempt
def generalstat(request):
    user_token = request.POST['token']
    user_id = User.objects.filter(token__token=user_token).get()
    income = Income.objects.filter(user = user_id).aggregate(Count('amount'), Sum('amount'))
    expense = Expence.objects.filter(user = user_id).aggregate(Count('amount'), Sum('amount'))
    conext = {}
    conext['expense'] = expense
    conext['income'] = income
    return JsonResponse(conext, encoder=JSONEncoder)




