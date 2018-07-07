#!/usr/bin/env python
""" The sound box application is basically a logger and a door keeper. """

import time
import re
import os
import datetime

from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email import encoders
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from subprocess import call
from threading import Timer
import smtplib
# import logging
import serial
import ephem
import xlsxwriter
from django.utils import timezone
import models as mod


class SoundBox(object):
    """ This is where sensors get read and time for closing and opening of
    door is calculated. """

    cmd_list = (['init', ''], ['inside_dht', 'a'], ['outside_dht', 'b'],
                ['close_door', 'c'], ['open_door', 'o'],
                ['servo_pos', 'd'], ['gas_power_on', 'e'],
                ['gas_power_off', 'f'], ['ammonia', 'g'],
                ['carbon_monoxide', 'h'], ['nitrogen_dioxide', 'i'],
                ['propane', 'j'], ['iso-butane', 'k'], ['methane', 'l'],
                ['hydrogen', 'm'], ['ethanol', 'n'], ['R0_0', 'p'],
                ['R0_1', 'q'], ['R0_2', 'r'], ['Rs_0', 's'], ['Rs_1', 't'],
                ['Rs_2', 'u'], ['fan_on', 'v'], ['fan_off', 'w'])
    comm = None

    def __init__(self):
        """ Initialize all the variables. """

        self.cmd_active = False
        self.servo_active = False
        self.is_it_day = False
        self.dht_interval = 60*5  # 5 Minutes intervals
        self.gas_state = None

        geo = mod.GeoLocation.objects.last()
        self.latitude = geo.latitude
        self.longitude = geo.longitude
        self.elevation = geo.elevation

        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # log_file = os.path.join(dir_path, 'static/sbox/log.txt')
        # logging.basicConfig(filename=log_file, filemode='w',
        #                    format='%(asctime)s %(message)s',
        #                    level=logging.DEBUG)
        # logging.info('Log start')

        # self.send_msg("sunrise")
        self.comm_init()
        dht_timer = Timer(self.dht_interval, self.read_dhts)
        dht_timer.start()

        t_sunset, t_sunrise = self.get_next_time_setting()
        if t_sunset < t_sunrise:
            self.cmd_send('open_door')
            t_s = Timer(t_sunset, self.sunset)
            self.is_it_day = True
        else:
            self.cmd_send('close_door')
            t_s = Timer(t_sunrise, self.sunrise)
            self.is_it_day = False

        t_s.start()

    def comm_init(self):
        """ Try initializing the uart if available. """

        try:
            self.comm = serial.Serial('/dev/tty96B0', 115200)
            data = self.comm.readline()
            print self.comm
            print data
        except ValueError:
            print 'Failed to find Serial port'
            self.comm = None

    def cmd_send(self, cmd='init'):
        """ Send the different commands via UART to the Arduino."""

        error = True

        # logging.info('cmd_send '+cmd)

        cnt = 0
        while self.cmd_active:
            time.sleep(0.5)
            if cnt > 100:
                # logging.info('cmd_send timeout error')
                return error, ''
            else:
                cnt += 1

        self.cmd_active = True

        for valid_cmd in self.cmd_list:
            if cmd == valid_cmd[0]:
                self.comm.write(valid_cmd[1])
                # logging.info('cmd_send tx: '+valid_cmd[1])
                break
        else:
            # logging.info('cmd_send unknown cmd')
            self.cmd_active = False
            return error, ''

        data = self.comm.readline()

        # logging.info('cmd_send rx: '+data)

        self.cmd_active = False
        error = False

        return error, data

    def gas_sensor(self):
        ''' Read and store the gas sensor data. '''

        if self.gas_state is None:
            # logging.info('gas_sensor power on')
            self.cmd_send('gas_power_on')
            self.gas_state = 'on'

            return 0

        elif self.gas_state == 'on':
            gas = mod.GasMeasure()
            print 'gas_sensor reading the different gases'

            # The U. S. Occupational Safety and Health Administration (OSHA) has
            # set a 15-minute exposure limit for gaseous ammonia of 35 ppm by
            # volume in the environmental air and an 8-hour exposure limit of
            # 25 ppm by volume.
            error, data = self.cmd_send('ammonia')

            ammonia = 0
            if error is False:
                ammonia = float(data)
                gas.ammonia = ammonia
                print 'ammonia concentration: ', ammonia

            # 8636 ppm (rat, 15 min), 5207 ppm (rat, 30 min), 1784 ppm
            # (rat, 4 hr)
            # 2414 ppm (mouse, 4 hr), 5647 ppm (guinea pig, 4 hr)
            error, data = self.cmd_send('carbon_monoxide')

            if error is False:
                gas.carbon_monoxide = float(data)
                print 'Carbon Monoxide concentration: ', gas.carbon_monoxide

            # 30 ppm (guinea pig, 1 hr), 315 ppm (rabbit, 15 min),
            # 68 ppm (rat, 4 hr), 138 ppm (rat, 30 min),
            # 1000 ppm (mouse, 10 min)
            error, data = self.cmd_send('nitrogen_dioxide')

            if error is False:
                gas.nitrogen_dioxide = float(data)
                print 'Nitrogen dioxide concentration: ', gas.nitrogen_dioxide

            # PEL (Permissible)	TWA 1000 ppm (1800 mg/m3)[3]
            # REL (Recommended)	TWA 1000 ppm (1800 mg/m3)[3]
            # IDLH (Immediate danger)	2100 ppm[3]
            error, data = self.cmd_send('propane')

            if error is False:
                gas.propane = float(data)
                print 'Propane concentration: ', gas.propane

            error, data = self.cmd_send('iso-butane')

            if error is False:
                gas.iso_butane = float(data)
                print 'Iso-butane concentration: ', gas.iso_butane

            error, data = self.cmd_send('methane')

            if error is False:
                gas.methane = float(data)
                print 'Methane concentration: ', gas.methane

            error, data = self.cmd_send('hydrogen')

            if error is False:
                gas.hydrogen = float(data)
                print 'Hydrogen concentration: ', gas.hydrogen

            error, data = self.cmd_send('ethanol')

            if error is False:
                gas.ethanol = float(data)
                print 'Ethanol concentration: ', gas.ethanol

            gas.save()

            return ammonia

        return 0

    def read_dhts(self):
        ''' Read and store the temperature and humidity sensors.'''

        r_t = Timer(self.dht_interval, self.read_dhts)
        r_t.start()

        error, data = self.cmd_send('inside_dht')

        inside_temperature = 70

        if error is False:
            data = re.sub('\n\r', '', data)
            data = re.split(' ', data)

            if len(data) < 2:
                print 'read_dhts incomplete DHT data', data
                return

            inside_temperature = (float(data[1])*1.8)+32
            dht = mod.Inside_DHT(Temperature=inside_temperature,
                                 Humidity=data[0])
            dht.save()

            print 'Inside dht', data

        error, data = self.cmd_send('outside_dht')

        if error is False:
            data = re.sub('\n\r', '', data)
            data = re.split(' ', data)

            if len(data) < 2:
                print 'read_dhts incomplete DHT data', data
                return

            outside_temperature = (float(data[1])*1.8)+32
            dht = mod.Outside_DHT(Temperature=outside_temperature,
                                  Humidity=data[0])
            dht.save()

            print 'Outside dht', data

        ammonia = self.gas_sensor()

        if(self.is_it_day is False) and (ammonia >= 15 or inside_temperature >= 70):
            self.cmd_send('fan_on')
        elif self.is_it_day and inside_temperature >= outside_temperature and inside_temperature >= 70:
            self.cmd_send('fan_on')
        else:
            self.cmd_send('fan_off')

    def max_min_dht(self):
        """ Determine the max and min temperature and humidity for
        the different sensors. """

        last = mod.DoorState.objects.last()
        inside_dht = mod.Inside_DHT.objects.filter(now__gte=last.now)

        max_temp = inside_dht[0].Temperature
        max_temp_date = inside_dht[0].now
        min_temp = inside_dht[0].Temperature
        min_temp_date = inside_dht[0].now
        max_hum = inside_dht[0].Humidity
        max_hum_date = inside_dht[0].now
        min_hum = inside_dht[0].Humidity
        min_hum_date = inside_dht[0].now

        for inside in inside_dht:
            if inside.Temperature > max_temp:
                max_temp = inside.Temperature
                max_temp_date = inside.now
            elif inside.Temperature < min_temp:
                min_temp = inside.Temperature
                min_temp_date = inside.now

            if inside.Humidity > max_hum:
                max_hum = inside.Humidity
                max_hum_date = inside.now
            elif inside.Humidity < min_hum:
                min_hum = inside.Humidity
                min_hum_date = inside.now

        maxmin_in = mod.MaxMinDHT(max_temp=max_temp, min_temp=min_temp,
                                  max_humidity=max_hum,
                                  min_humidity=min_hum)

        maxmin_in.max_temp_date = max_temp_date
        maxmin_in.min_temp_date = min_temp_date
        maxmin_in.max_humidity_date = max_hum_date
        maxmin_in.min_humidity_date = min_hum_date

        maxmin_in.inside = True
        maxmin_in.day = self.is_it_day
        maxmin_in.save()

        outside_dht = mod.Outside_DHT.objects.filter(now__gte=last.now)

        max_temp = outside_dht[0].Temperature
        max_temp_date = outside_dht[0].now
        min_temp = outside_dht[0].Temperature
        min_temp_date = outside_dht[0].now
        max_hum = outside_dht[0].Humidity
        max_hum_date = outside_dht[0].now
        min_hum = outside_dht[0].Humidity
        min_hum_date = outside_dht[0].now

        for inside in outside_dht:
            if inside.Temperature > max_temp:
                max_temp = inside.Temperature
                max_temp_date = inside.now
            elif inside.Temperature < min_temp:
                min_temp = inside.Temperature
                min_temp_date = inside.now

            if inside.Humidity > max_hum:
                max_hum = inside.Humidity
                max_hum_date = inside.now
            elif inside.Humidity < min_hum:
                min_hum = inside.Humidity
                min_hum_date = inside.now

        maxmin_out = mod.MaxMinDHT(max_temp=max_temp, min_temp=min_temp,
                                   max_humidity=max_hum, min_humidity=min_hum)

        maxmin_out.max_temp_date = max_temp_date
        maxmin_out.min_temp_date = min_temp_date
        maxmin_out.max_humidity_date = max_hum_date
        maxmin_out.min_humidity_date = min_hum_date
        maxmin_out.inside = False
        maxmin_out.day = self.is_it_day
        maxmin_out.save()

        print maxmin_in, maxmin_out

        return maxmin_in, maxmin_out

    def get_next_time_setting(self):
        """ Find the next time for sunset and sunrise. """

        home = ephem.Observer()

        home.lat = str(self.latitude)
        home.lon = str(self.longitude)
        home.elev = self.elevation

        home.date = ephem.now()
        t_sunrise = home.next_rising(ephem.Sun())
        t_sunset = home.next_setting(ephem.Sun())

        print 'Home date ', home.date, t_sunset, t_sunrise

        t_sunset = t_sunset - home.date
        print 'Time to next sunset in days = ', t_sunset

        t_sunset = t_sunset*24*60*60
        print 'Time to next sunset in seconds = ', t_sunset

        t_ss = time.gmtime(t_sunset + time.time())
        print 'gmtime to next sunset = ', t_ss

        # Add or close the door some time after the actual sunset.
        t_sunset += 60*60

        t_sunrise = t_sunrise - home.date
        print 'Time to next sunrise in days = ', t_sunrise

        t_sunrise = t_sunrise*24*60*60
        print 'Time to sunrise in seconds = ', t_sunrise

        t_sr = time.gmtime(t_sunrise + time.time())
        print 'gmtime to next sunrise = ', t_sr

        # Fix the hours to 8
        print 'time.daylight: ', time.daylight
        if time.daylight:
            t_sunrise += (15 - t_sr.tm_hour)*60*60
            print 'daylight in effect', t_sr.tm_hour
        else:
            t_sunrise += (15 - t_sr.tm_hour)*60*60

        # Fix the minutes to 30
        if t_sr.tm_min > 30:
            t_sunrise -= (t_sr.tm_min - 30)*60
        else:
            t_sunrise += (30 - t_sr.tm_min)*60

        t_sr = time.gmtime(t_sunrise + time.time())
        print 'fix gmtime to next sunrise = ', t_sr

        # Next lines for testing only
        # t_sunset = 60*6
        # t_sunrise = 60*6-10
        # print 'Exiting', t_sunset, t_sunrise

        return t_sunset, t_sunrise

    def send_msg(self, body_msg, image=None, image2=None, maxmin_in=None,
                 maxmin_out=None):
        """ Send a message with pictures and data. """

        print "send_msg", body_msg
        t_s = time.gmtime()

        for email in mod.Email.objects.all():
            msg_from = email.from_email
            msg_to = email.to_email
            msg = MIMEMultipart()
            msg['From'] = msg_from
            msg['To'] = msg_to
            msg['Subject'] = "Lucky & Miracle: " + body_msg

            body = body_msg
            if maxmin_in is not None:
                body += '\nThe maximum temperature measured inside was '
                body += str(maxmin_in.max_temp) + 'F at '
                body += maxmin_in.max_temp_date.strftime('%y/%m/%d %H:%M:%S') + '\n'
                body += '\nThe minimum temperature measured inside was ' + str(maxmin_in.min_temp)
                body += 'F at ' + maxmin_in.min_temp_date.strftime('%y/%m/%d %H:%M:%S') + '\n'

            if maxmin_out is not None:
                body += '\nThe maximum temperature measured outside was '
                body += str(maxmin_out.max_temp) + 'F at '
                body += maxmin_out.max_temp_date.strftime('%y/%m/%d %H:%M:%S') + '\n'
                body += '\nThe minimum temperature measured outside was '
                body += str(maxmin_out.min_temp) + 'F at '
                body += maxmin_out.min_temp_date.strftime('%y/%m/%d %H:%M:%S') + '\n'

            msg.attach(MIMEText(body, 'plain'))
            if image is not None:
                f_p = open(image, 'rb')
                img = MIMEImage(f_p.read())
                f_p.close()
                msg.attach(img)

            if image2 is not None:
                f_p = open(image2, 'rb')
                img = MIMEImage(f_p.read())
                f_p.close()
                msg.attach(img)

            if t_s.tm_wday == 6 and re.search('sunrise', body_msg):
                report_file = self.report()
                f_p = open(report_file, 'rb')
                report = MIMEBase('application', 'octet-stream')
                report.set_payload(f_p.read())
                f_p.close()
                encoders.encode_base64(report)
                report.add_header("Content-Disposition", "attachment", filename='report.xlsx')
                msg.attach(report)

            try:
                # if True:
                hotmail = smtplib.SMTP('smtp.live.com', 587)
                hotmail.starttls()
                hotmail.login(msg_from, email.from_password)
                text = msg.as_string()
                hotmail.sendmail(msg_from, msg_to, text)
                hotmail.quit()
            except (RuntimeError, TypeError, NameError):
                print "Email:", RuntimeError, TypeError, NameError
            except ValueError:
                print "Email ValueError", ValueError

    def sunset(self):
        """ Close the door at sunset, send an email and setup sunrise. """

        t_sr, t_sunrise = self.get_next_time_setting()
        t_sr = Timer(t_sunrise, self.sunrise)
        t_sr.start()

        while self.servo_active:
            time.sleep(.2)

        self.servo_active = True

        error, data = self.cmd_send('close_door')

        self.servo_active = False

        maxmin_in, maxmin_out = self.max_min_dht()

        d_s = mod.DoorState(door_open=False, servo_pos=int(data))
        d_s.save()

        self.is_it_day = False

        if error is False:
            self.send_msg('Sunset', maxmin_in=maxmin_in, maxmin_out=maxmin_out)
        else:
            data = re.sub('\n\r', '', data)
            self.send_msg('Sunset: error '+data, maxmin_in=maxmin_in,
                          maxmin_out=maxmin_out)

    def sunrise(self):
        """At sunrise we want to open the door. """

        t_sunset, t_sr = self.get_next_time_setting()
        t_sr = Timer(t_sunset, self.sunset)
        t_sr.start()

        while self.servo_active:
            time.sleep(0.2)

        dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        start_image = os.path.join(dir_path, 'sbox/static/sbox/pictures/start.jpg')
        call(['fswebcam', '-S', '100', '-r', '1280x720', start_image])

        self.servo_active = True

        self.cmd_send('open_door')
        # open the door twice in case it is stuck.
        error, data = self.cmd_send('open_door')

        self.servo_active = False

        end_image = os.path.join(dir_path, 'sbox/static/sbox/pictures/end.jpg')
        call(['fswebcam', '-S', '100', '-r', '1280x720', end_image])

        data = re.sub('\n\r', '', data)

        maxmin_in, maxmin_out = self.max_min_dht()

        d_s = mod.DoorState(door_open=True, servo_pos=int(data))
        d_s.save()

        self.is_it_day = True

        if error is False:
            self.send_msg('Sunrise', start_image, end_image,
                          maxmin_in=maxmin_in, maxmin_out=maxmin_out)
        else:
            self.send_msg('Sunrise error: '+data, start_image, end_image,
                          maxmin_in=maxmin_in, maxmin_out=maxmin_out)

    def report(self):
        ''' Make a weekly report and send it on Sunday. '''

        dir_p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file = os.path.join(dir_p, 'sbox/static/sbox/pictures/report.xlsx')
        book = xlsxwriter.Workbook(report_file)
        sheet = book.add_worksheet("Raw Data")
        header = ["Date", "Inside Temperature", "Outside Temperature",
                  "Inside Humidity", "Outside Humidity", "Ammonia",
                  "Carbon Monoxide", "Nitrogen dioxide", "Propane",
                  "Iso-butane", "Methane", "Hydrogen", "Ethanol"]

        last_7_days = timezone.now() - datetime.timedelta(days=7)
        i_w_t = mod.Inside_DHT.objects.filter(now__gte=last_7_days)
        o_w_t = mod.Outside_DHT.objects.filter(now__gte=last_7_days)
        o_w_g = mod.GasMeasure.objects.filter(now__gte=last_7_days)

        for i, head in enumerate(header):
            sheet.write_string(0, i, head)
            sheet.set_column(i, i, len(head))

        max_in_temp = 0
        max_out_temp = 0
        max_ammonia = 0
        min_in_temp = 110
        min_out_temp = 110
        min_ammonia = 110

        for i, data in enumerate(i_w_t):
            sheet.write(i+1, 0, str(data.now))
            sheet.write(i+1, 1, data.Temperature)
            sheet.write(i+1, 3, data.Humidity)

            if data.Temperature > max_in_temp:
                max_in_temp = data.Temperature

            elif data.Temperature < min_in_temp:
                min_in_temp = data.Temperature

            if len(o_w_t) > i:
                sheet.write(i+1, 2, o_w_t[i].Temperature)
                sheet.write(i+1, 4, o_w_t[i].Humidity)

                if o_w_t[i].Temperature > max_out_temp:
                    max_out_temp = o_w_t[i].Temperature

                elif o_w_t[i].Temperature < min_out_temp:
                    min_out_temp = o_w_t[i].Temperature

            if len(o_w_g) > i:
                sheet.write(i+1, 5, o_w_g[i].ammonia)
                sheet.write(i+1, 6, o_w_g[i].carbon_monoxide)
                sheet.write(i+1, 7, o_w_g[i].nitrogen_dioxide)
                sheet.write(i+1, 8, o_w_g[i].propane)
                sheet.write(i+1, 9, o_w_g[i].iso_butane)
                sheet.write(i+1, 10, o_w_g[i].methane)
                sheet.write(i+1, 11, o_w_g[i].hydrogen)
                sheet.write(i+1, 12, o_w_g[i].ethanol)

                if o_w_g[i].ammonia > max_ammonia:
                    max_ammonia = o_w_g[i].ammonia

                elif o_w_g[i].ammonia < min_ammonia:
                    min_ammonia = o_w_g[i].ammonia

        sheet = book.add_worksheet("Graphs")

        chart = book.add_chart({'type': 'line'})
        chart.set_title({'name': 'Inside Temperature'})
        chart.set_legend({'none': True})
        chart.set_x_axis({'name': 'Days', 'date_axis': True})
        chart.set_y_axis({'name': 'Temperature', 'max': max_in_temp,
                          'min': min_in_temp})
        chart.set_size({'x_scale': 3, 'y_scale': 2})
        chart.add_series({'categories': ['Raw Data', 1, 0, i, 0],
                          'values': ['Raw Data', 1, 1, i, 1],
                          'line': {'color': 'green'}})
        sheet.insert_chart('A1', chart)

        chart = book.add_chart({'type': 'line'})
        chart.set_title({'name': 'Outside Temperature'})
        chart.set_legend({'none': True})
        chart.set_x_axis({'name': 'Days', 'date_axis': True})
        chart.set_y_axis({'name': 'Temperature', 'max': max_out_temp,
                          'min': min_out_temp})
        chart.set_size({'x_scale': 3, 'y_scale': 2})
        chart.add_series({'categories': ['Raw Data', 1, 0, i, 0],
                          'values': ['Raw Data', 1, 2, i, 2],
                          'line': {'color': 'blue'}})
        sheet.insert_chart('A31', chart)

        chart = book.add_chart({'type': 'line'})
        chart.set_title({'name': 'Inside vs. Outside'})
        chart.set_legend({'none': True})
        chart.set_x_axis({'name': 'Days', 'date_axis': True})
        chart.set_y_axis({'name': 'Temperature', 'max': max_out_temp,
                          'min': min_out_temp})
        chart.set_size({'x_scale': 3, 'y_scale': 2})
        chart.add_series({'categories': ['Raw Data', 1, 0, i, 0],
                          'values': ['Raw Data', 1, 1, i, 1],
                          'line': {'color': 'green'}})
        chart.add_series({'values': ['Raw Data', 1, 2, i, 2],
                          'line': {'color': 'blue'}})
        sheet.insert_chart('A62', chart)

        chart = book.add_chart({'type': 'line'})
        chart.set_title({'name': 'Ammonia'})
        chart.set_legend({'none': True})
        chart.set_x_axis({'name': 'Days', 'date_axis': True})
        chart.set_y_axis({'name': 'ppm', 'max': max_ammonia,
                          'min': min_ammonia})
        chart.set_size({'x_scale': 3, 'y_scale': 2})
        chart.add_series({'categories': ['Raw Data', 1, 0, i, 0],
                          'values': ['Raw Data', 1, 5, i, 5],
                          'line': {'color': 'red'}})
        sheet.insert_chart('A93', chart)

        book.close()

        return report_file
