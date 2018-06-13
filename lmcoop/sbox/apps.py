''' This controls the sensors connected to the sound box. '''

# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

from threading import Timer
from django.apps import AppConfig


class SboxConfig(AppConfig):
    """ Django provides this for app configuration. """

    name = 'sbox'
    print 'sbox init'

    def ready(self):
        """ import here to avoid other issues. It is
        atypical but needed. """

        import sbox

        t_sbox = Timer(60, sbox.SoundBox)
        t_sbox.start()
