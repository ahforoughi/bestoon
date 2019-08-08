# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Expence
from .models import Income

# Register your models here.
admin.site.register(Expence)
admin.site.register(Income)
