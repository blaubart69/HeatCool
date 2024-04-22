import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO_PIN = 15
GPIO.setup(GPIO_PIN,GPIO.IN,GPIO.PUD_UP)

liter_per_signal        = 5
ns_per_hour             = 3600 * 1000 * 1000 * 1000
ns_per_hour_times_liter = ns_per_hour * liter_per_signal

last_ns = None

def onSignal(null):
    global last_ns
    curr_ns = time.monotonic_ns()

    if last_ns != None:
        diff_ns = curr_ns - last_ns
        liter_perhour = int ( ns_per_hour_times_liter / diff_ns )
        diff_s = diff_ns / 1000000000
        print(f'seconds/{liter_per_signal}l: {diff_s:8.3f}\t{liter_perhour:8} l/h')
    
    last_ns = curr_ns

GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=onSignal, bouncetime=50)
#GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=onSignal)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
