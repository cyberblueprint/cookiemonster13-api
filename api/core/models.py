# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import collections
import json

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from jsonfield import JSONField


@python_2_unicode_compatible
class Home(models.Model):
    json = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict})
    created_at = models.DateTimeField(auto_now_add=True, editable=True, verbose_name="Created")
    updated_at = models.DateTimeField(auto_now=True, editable=True, verbose_name="Updated")

    def __str__(self):
        data = json.dumps(self.json)
        return data[:51] + '...' if len(data) > 50 else data
