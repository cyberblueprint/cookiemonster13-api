# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from .models import Home


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at', 'updated_at')

