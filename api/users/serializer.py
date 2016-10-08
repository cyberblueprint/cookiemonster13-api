# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework import serializers

from .models import User


class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
    friends = FriendsSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'friends')
