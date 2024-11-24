import RPi.GPIO as GPIO # !!! pip install rpi-lgpio !!!
import time
import datetime
import sys
import locale

locale.setlocale(locale.LC_ALL, '')

liter_per_signal        = 10 
ns_per_hour             = 3600 * 1000 * 1000 * 1000
ns_per_hour_times_liter = ns_per_hour * liter_per_signal

class SignalContext:
    last_ns = None
    timespan = [None, None]
    write_idx = 0

ctx=SignalContext()

def ns_to_s(ns : int):
    return ns / 1000000000

def onSignal(null):
    global ctx
    curr_ns = time.monotonic_ns()

    if ctx.last_ns != None:
        one_signal_ns = curr_ns - ctx.last_ns
        liter_perhour = int ( ns_per_hour_times_liter / one_signal_ns )

        print(f'{liter_perhour:>8} l/h '
              f'\t{(locale.format_string("%.2f", ns_to_s(one_signal_ns), True)):>8} s/{liter_per_signal}l' 
              f'\t{datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")}')

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


if 'fake' in sys.argv:
    fakeloop()
else:
    GPIO.setmode(GPIO.BCM)
    GPIO_PIN = 18
    GPIO.setup(GPIO_PIN,GPIO.IN,GPIO.PUD_UP)
    GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=onSignal, bouncetime=50)
    print(f'set pin {GPIO_PIN}. entering loop...')
    mainloop()
