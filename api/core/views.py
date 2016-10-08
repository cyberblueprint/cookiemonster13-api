# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import time

from django.core.files import File
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.utils.timezone import now
from django.core.cache import cache
from django.contrib.staticfiles.templatetags.staticfiles import static

from rest_framework import views
from rest_framework.response import Response
import xmltodict

from api.users.models import User
from config.settings.common import STATICFILES_DIRS, STATIC_ROOT, DEBUG


class FootballListView(views.APIView):
    authentication_classes = ()
    permission_classes = ()
    query_filters = (
        'date__gte',
        'date__gt',
        'date__lte',
        'date__lt',
        'date__in',
    )

    @staticmethod
    def get_matchs_xml(request):

        path = STATIC_ROOT if DEBUG else STATICFILES_DIRS[0]
        path += '/data/scotland_football.xml'
        success = True
        try:
            with open(str(path), 'r') as f:
                xml_file = File(f)
                data = dict(xmltodict.parse(xml_file.read()))
        except Exception as e:
            data = {'error': str(e)}
            success = False

        return data, success

    def _get_winner(self, match):
        self.local_goals = int(match["localGoals"])
        self.visitor_goals = int(match["visitorGoals"])

        if self.local_goals > self.visitor_goals:
            return match["local"]["#text"]
        elif self.visitor_goals > self.local_goals:
            return match["visitor"]["#text"]
        else:
            return 'Draw'

    @staticmethod
    def _format_date(match_time, match_date):
        year = match_date[:4]
        month = match_date[4:6]
        day = match_date[6:]
        return (
            '{time}'.format(time=match_time),
            '{day}-{month}-{year}'.format(day=day, month=month, year=year)
        )

    @staticmethod
    def _compare_dates(query_filter, date_1, date_2):
        if query_filter == 'date__gt':
            return date_1 > date_2
        elif query_filter == 'date__gte':
            return date_1 >= date_2
        elif query_filter == 'date__lt':
            return date_1 < date_2
        elif query_filter == 'date__lte':
            return date_1 <= date_2
        elif query_filter == 'date__in':
            low_date_2, hig_date_2 = date_2.split(',')
            return low_date_2 <= date_1 <= hig_date_2

    def _get_matches(self, fixture, query=None):
        query_filter = None
        for key in query.keys():
            if key in self.query_filters:
                query_filter = key

        matches = []
        for dates in fixture["date"]:
            for match in dates["match"]:
                try:
                    hour, date = self._format_date(match["@time"], match["@date"])
                    try:
                        if query_filter and not self._compare_dates(query_filter, date, query.get(query_filter)):
                            continue
                    except Exception:
                        continue

                    local = match["local"]["#text"]
                    visitor = match["visitor"]["#text"]
                    winner = self._get_winner(match)
                    teams = '{} - {}, winner: {}'.format(local, visitor, winner)
                    matches.append(
                        {
                            "match": teams,
                            "result": "{} - {}".format(self.local_goals, self.visitor_goals),
                            "date": "{} {}".format(hour, date)
                        }
                    )
                except (KeyError, TypeError):
                    continue
        return matches

    def get(self, request, format=None):
        """
        {
            "match": "Celtic - Dundee", "winner": "Celtic",
            "result": "1 - 0",
            "date": "10:50 12-02-2015"
        },
        :param request:
        :param format:
        :return:
        """

        duration = time.time() - request.start_time
        xml_data, success = cache.get_or_set('xml_data', self.get_matchs_xml(request), 5)

        if not success:
            matches = ()
            error = xml_data["error"]
        else:
            error = ''
            matches = cache.get_or_set('matches', self._get_matches(xml_data["fixture"], request.GET), 5)

        response_data = {
            "datetime": str(now()),
            "completed_in": str(duration) + ' seconds',
            "matches": matches,
            "error": error
        }
        return Response(response_data)


def matchs(request):
    matchs_xml = static('data/scotland_football.xml')
    return HttpResponseRedirect(redirect_to=matchs_xml, content_type="application/xhtml+xml")


class CreateUserView(TemplateView):
    template_name = 'pages/home.html'

    def get(self, request, *args, **kwargs):
        total_user = User.objects.count()
        if total_user > 25:
            return HttpResponse('We have already users.')

        for i in range(1, 26):
            username = 'user' + str(i)
            email = username + '@e.com'
            data = (username, email, 'Qwerty1!')
            User.objects.create_user(*data)

        return HttpResponse('Users created.')
