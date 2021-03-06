""" Models for the different data to store. """
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# from datetime import datetime


class Inside_DHT(models.Model):
    """ Store the temperature and humidity from the sensor. """
    Temperature = models.FloatField(default=60)
    Humidity = models.FloatField(default=40)
    now = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """ Display these values in admin. """
        return "T:" + str(self.Temperature) + " H:" + str(self.Humidity) +\
               " " + str(self.now)


class Outside_DHT(models.Model):
    """ Store the temperature and humidity from the sensor. """
    Temperature = models.FloatField(default=60)
    Humidity = models.FloatField(default=40)
    now = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """ Display these values in admin. """
        return "T:" + str(self.Temperature) + " H:" + str(self.Humidity) +\
               " " + str(self.now)


class MaxMinDHT(models.Model):
    """ Store the maximun and minimum temperature and humidity for
    the day or night. """
    max_temp = models.FloatField(default=60)
    max_temp_date = models.DateTimeField(unique_for_date=True)
    min_temp = models.FloatField(default=60)
    min_temp_date = models.DateTimeField(unique_for_date=True)
    max_humidity = models.FloatField(default=60)
    max_humidity_date = models.DateTimeField(unique_for_date=True)
    min_humidity = models.FloatField(default=60)
    min_humidity_date = models.DateTimeField(unique_for_date=True)
    inside = models.BooleanField(default=True)
    day = models.BooleanField(default=True)

    def __str__(self):
        """ Display these values in admin. """
        return 'Max temp = ' + str(self.max_temp) + ', Min temp = ' +\
               str(self.min_temp) + ', inside ' + str(self.inside) +\
               ', day ' + str(self.day)


class DoorState(models.Model):
    """ Store the time the door closed or opened. """
    now = models.DateTimeField(auto_now_add=True)
    door_open = models.BooleanField(default=True)
    servo_pos = models.IntegerField(default=60)
    start_image = models.CharField(default="", max_length=254)
    end_image = models.CharField(default="", max_length=254)

    def __str__(self):
        """ Display these values in admin. """
        return str(self.door_open) + ' ' + str(self.servo_pos) +\
            str(self.start_image) + ' ' + str(self.now)


class Email(models.Model):
    """ Store the emails to send information and pictures. """
    from_email = models.EmailField(max_length=100)
    from_password = models.CharField(max_length=100)
    to_email = models.EmailField(max_length=100)

    def __str__(self):
        """ Display these values in admin. """
        return "From: " + self.from_email + " To: " + self.to_email


class GeoLocation(models.Model):
    """ Set the location of the sbox to calulate sunrise and sunset. """
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    elevation = models.FloatField(default=0)

    def __str__(self):
        """ Display these values in admin. """
        return 'latitude = ' + str(self.latitude) + ' longitude = ' +\
            str(self.longitude) + ' elevation = ' + str(self.elevation)


class GasMeasure(models.Model):
    """ Store the levels of the different gases. """
    now = models.DateTimeField(auto_now_add=True)
    ammonia = models.FloatField(default=0)
    carbon_monoxide = models.FloatField(default=0)
    nitrogen_dioxide = models.FloatField(default=0)
    propane = models.FloatField(default=0)
    iso_butane = models.FloatField(default=0)
    methane = models.FloatField(default=0)
    hydrogen = models.FloatField(default=0)
    ethanol = models.FloatField(default=0)
    R0_0 = models.FloatField(default=0)
    R0_1 = models.FloatField(default=0)
    R0_2 = models.FloatField(default=0)
    Rs_0 = models.FloatField(default=0)
    Rs_1 = models.FloatField(default=0)
    Rs_2 = models.FloatField(default=0)

    def __str__(self):
        """ Display these values in admin. """
        return str(self.now) + ' Ammonia = ' + str(self.ammonia) + ', carbon monoxide = ' +\
            str(self.carbon_monoxide) + ', nitrogen dioxide = ' +\
            str(self.nitrogen_dioxide) + ', propane = ' +\
            str(self.propane) + ', iso-butane = ' + str(self.iso_butane) +\
            ', methane = ' + str(self.methane) + ', hydrogen = ' +\
            str(self.hydrogen) + ', ethanol = ' + str(self.ethanol)
