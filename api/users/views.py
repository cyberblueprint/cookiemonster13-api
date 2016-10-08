# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import time

from django.utils.timezone import now
from django.core.cache import cache

from rest_framework import generics

from .models import User
from .serializer import UserSerializer


class UserListViewSet(generics.ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        response = super(UserListViewSet, self).list(request, *args, **kwargs)
        duration = time.time() - self.request.start_time
        response_data = cache.get_or_set('user_list_data', response.data, 5)
        data = (
            {
                "datetime": str(now()),
                "completed_in": str(duration) + ' seconds',
                "data": response_data,
            }
        )

        response.data = data
        return response
