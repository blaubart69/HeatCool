import RPi.GPIO as GPIO
import time
import datetime
import sys
import locale

import influxdb_client

locale.setlocale(locale.LC_ALL, '')

GPIO.setmode(GPIO.BCM)

GPIO_PIN = 15
GPIO.setup(GPIO_PIN,GPIO.IN,GPIO.PUD_UP)

liter_per_signal        = 5
liter_per_two_signals   = 10
ns_per_hour             = 3600 * 1000 * 1000 * 1000
ns_per_hour_times_two_signals = ns_per_hour * liter_per_two_signals

class SignalContext:
    last_ns = None
    timespan = [None, None]
    write_idx = 0

    def __init__(self, influxwriteapi):
        self.write_api = influxwriteapi

client = influxdb_client.InfluxDBClient(
    url='http://localhost:8086/',
    token='yFvyHYtAHdDoiFJcVxPnFbSVNzRwINmd5PApkVMCygTLAd6bnlDCfRql_ibWvHjpGjAiNUr21fKvOH0M6XZvog==',
    org='orgbee'
)

write_api = client.write_api(write_options=influxdb_client.client.write_api.SYNCHRONOUS)
ctx=SignalContext(write_api)

def ns_to_s(ns : int):
    return ns / 1000000000

def onSignal(null):
    global ctx
    curr_ns = time.monotonic_ns()

    if ctx.last_ns != None:
        ctx.write_idx = 1 - ctx.write_idx
        ctx.timespan[ctx.write_idx] = curr_ns - ctx.last_ns

    if ctx.timespan[0] != None and ctx.timespan[1] != None:
        one_rotation_ns = ctx.timespan[0] + ctx.timespan[1]
        liter_perhour = int ( ns_per_hour_times_two_signals / one_rotation_ns )

        print(f'{liter_perhour:>8} l/h '
              f'\t{(locale.format_string("%.2f", ns_to_s(one_rotation_ns), True)):>8} s/{liter_per_two_signals}l:' 
              f'\t{(locale.format_string("%.2f", ns_to_s(ctx.timespan[ctx.write_idx]))):>8} s last signal '
              f'\t{datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")}')

        p = influxdb_client.Point("water").field("literperhour", liter_perhour)
        ctx.write_api.write(bucket='wp', org='orgbee', record=p)

    ctx.last_ns = curr_ns

def fakeloop():
    while True:
        onSignal(23)
        time.sleep(1)

def mainloop():
    try:
        while True:
            time.sleep(600)
    except KeyboardInterrupt:
        GPIO.cleanup()
        write_api.close()
        client.close()


if 'fake' in sys.argv:
    fakeloop()
else:
    GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=onSignal, bouncetime=50)
    mainloop()
