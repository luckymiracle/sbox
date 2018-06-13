# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import models as mod

# Register your models here.
admin.site.register(mod.Inside_DHT)
admin.site.register(mod.Outside_DHT)
admin.site.register(mod.MaxMinDHT)
admin.site.register(mod.DoorState)
admin.site.register(mod.Email)
admin.site.register(mod.GasMeasure)
admin.site.register(mod.GeoLocation)
