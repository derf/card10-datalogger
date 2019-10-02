import utime
import display
import leds
import ledfx
import buttons
import light_sensor
import ujson
import os
import bme680

def blink_led(led):
    """
    Turns off leds, blinks given led for 100ms
    can be used as an indicator
    :param led: led to blink
    """
    leds.clear()
    utime.sleep(0.1)
    leds.set(led, [50, 50, 0])
    utime.sleep(0.1)
    leds.clear()

def get_bat_color(bat, v):
    """
    Function determines the color of the battery indicator. Colors can be set in config.
    Voltage threshold's are currently estimates as voltage isn't that great of an indicator for
    battery charge.
    :param bat: battery config tuple (boolean: indicator on/off, array: good rgb, array: ok rgb, array: bad rgb)
    :return: battery status tuple (float: battery voltage, false if old firmware, RGB color array otherwise)
    """
    try:
        if v > 3.7:
            return (v, bat[1])
        if v > 3.6:
            return (v, bat[2])
        return (v, bat[3])
    except AttributeError:
        return (0, False)


def render_battery(disp, bat, voltage):
    """
    Adds the battery indicator to the display. Does not call update or clear so it can be used in addition to
    other display code.
    :param disp: open display
    :param bat: battery config tuple (boolean: indicator on/off, array: good rgb, array: ok rgb, array: bad rgb)
    """
    v, c = get_bat_color(bat, voltage)
    if not c:
        return
    if v > 4.1:
        disp.rect(140, 2, 155, 9, filled=True, col=c)
    else:
        disp.rect(140, 2, 154, 9, filled=True, col=[0, 0, 0])
        disp.rect(140, 2, 154, 9, filled=False, col=c)
        if v > 3.5:
            disp.rect(141, 3, 142 + int((v - 3.5) * 20), 8, filled=True, col=c)
    disp.rect(155, 4, 157, 7, filled=True, col=c)

def run_loop():
    bat = [1, [0, 230, 00], [255, 215, 0], [255, 0, 0]]
    with display.open() as disp:
        disp.clear()
        disp.backlight(5)
        disp.print("@derfnull", posy=0)
        disp.update()
        disp.close()
    while True:
        sensor_data = bme680.get_data()
        ambient_light = light_sensor.get_reading()
        battery_voltage = os.read_battery()
        with display.open() as disp:
            render_battery(disp, bat, battery_voltage)
            disp.print("{:2.1f} C {:2.0f} %".format(sensor_data[0], sensor_data[1]), posy=20)
            disp.print("{:5.1f} hPa".format(sensor_data[2]), posy=40)
            disp.print("{:4.1f} kOhm".format(sensor_data[3] / 1000), posy=60)
            disp.update()
            disp.close()
        with open('sensorlog.txt', 'a') as f:
            f.write('{} {} {} {} {} {} {}\n'.format(utime.time(), sensor_data[0], sensor_data[1], sensor_data[2], sensor_data[3], ambient_light, battery_voltage))
        utime.sleep(10)

leds.clear()
bme680.init()
run_loop()
