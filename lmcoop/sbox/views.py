""" This module provides the different views. """
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import os
import datetime
from subprocess import call

from django.shortcuts import render
from django.utils import timezone
import models as mod


def home(request):
    """ This is the main or index view. """

    print "home page"
    last_24_hours = timezone.now() - datetime.timedelta(days=1)
    maxmin = mod.MaxMinDHT.objects.all()
    inside_dht = mod.Inside_DHT.objects.filter(now__gte=last_24_hours)
    outside_dht = mod.Outside_DHT.objects.filter(now__gte=last_24_hours)

    dht_temps = []
    dht_hums = []
    for i, data in enumerate(inside_dht):
        if len(outside_dht) > i:
            dht_temps.append({'now': data.now, 'inside': data.Temperature,
                              'outside': outside_dht[i].Temperature})
            dht_hums.append({'now': data.now, 'inside': data.Humidity,
                             'outside': outside_dht[i].Humidity})

    maxmin_inside = []
    maxmin_outside = []
    for data in maxmin:
        if data.inside:
            maxmin_inside.append({'date': data.max_temp_date,
                                  'temp': data.max_temp})
            maxmin_inside.append({'date': data.min_temp_date,
                                  'temp': data.min_temp})
        else:
            maxmin_outside.append({'date': data.max_temp_date,
                                   'temp': data.max_temp})
            maxmin_outside.append({'date': data.min_temp_date,
                                   'temp': data.min_temp})

    maxmin_inside.sort()
    maxmin_outside.sort()

    context = {'maxmin_inside': maxmin_inside, 'maxmin_outside': maxmin_outside,
               'dht_temps': dht_temps, 'dht_hums': dht_hums}

    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_name = os.path.join(dir_path, 'sbox/static/sbox/pictures/now.jpg')

    call(['fswebcam', '-S', '100', '-r', '1280x720', image_name])

    image_name = re.sub('/home/linaro/lmcoop/sbox/static', '', image_name)
    context['image'] = image_name

    return render(request, 'sbox/home.html', context)


def gas(request):
    """ This view provides the data for the different gases. """

    print "Gas page"

    context = {}
    last_24_hours = timezone.now() - datetime.timedelta(days=7)
    gas_data = mod.GasMeasure.objects.filter(now__gte=last_24_hours)
    # gas_data = GasMeasure.objects.all()

    ammonia = []
    carbon_monoxide = []
    nitrogen_dioxide = []
    for data in gas_data:
        ammonia.append({'now': data.now, 'ammonia': data.ammonia, 'safe': 25})
        carbon_monoxide.append({'now': data.now, 'carbon_monoxide': data.carbon_monoxide,
                                'safe': 8636})

        nitrogen_dioxide.append({'now': data.now, 'nitrogen_dioxide': data.nitrogen_dioxide,
                                 'safe': 68})

    context['ammonia'] = ammonia
    context['carbon_monoxide'] = carbon_monoxide
    context['nitrogen_dioxide'] = nitrogen_dioxide

    return render(request, 'sbox/gas.html', context)
