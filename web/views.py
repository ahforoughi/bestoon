# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from web.models import Token, User, Expence, Income
from datetime import datetime
# Create your views here.

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