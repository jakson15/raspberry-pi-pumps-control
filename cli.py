import argparse
import RPi.GPIO as GPIO
import json

def is_manual_mode():
    try:
        with open("config.json", "r") as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        print("Nie ma pliku config. Ustaw tryb manulny aby go stworzyć.")
        return False
    except:
        print("Wystąpił nieznany problem z plikiem ustawień")
        return False


def set_manual_mode(mode):
    data = is_manual_mode()
    if data:
        data["manual_mode"] = mode
        with open("config.json", "w") as json_file:
            json.dump(data, json_file, indent=4)
    else:
        new_data_file = {
            "manual_mode": 1
        }
        with open("config.json", "w") as json_file:
            json.dump(new_data_file, json_file, indent=4)

def pump_off(pin):
    GPIO.output(pin, GPIO.HIGH)

def pump_on(pin):
    GPIO.output(pin, GPIO.LOW)

def is_manual_mode():
    with open("config.json", "r") as json_file:
        data = json.load(json_file)
        return data["manual_mode"]

mode = GPIO.getmode()
if 11 != mode:
    GPIO.setmode(GPIO.BCM)

pumps_ports = {
    'dom': 13,
    'haft': 19,
    'firany': 26,
    'zapas': 6
}

for gpio_port in pumps_ports:
    usage = GPIO.gpio_function(pumps_ports[gpio_port])
    if 0 != usage:
        GPIO.setup(pumps_ports[gpio_port], GPIO.OUT)

parser = argparse.ArgumentParser()
parser.add_argument("--on", help="turn on pump", action="store_true")
parser.add_argument("--off", help="turn off pump", action="store_true")
parser.add_argument("--dom", help="name of pump", action="store_true")
parser.add_argument("--haft", help="name of pump", action="store_true")
parser.add_argument("--firany", help="name of pump", action="store_true")
parser.add_argument("--status", help="name of pump", action="store_true")
parser.add_argument("--manual", help="name of pump", action="store_true")

args = parser.parse_args()

if args.status:
    for gpio_port in pumps_ports:
        state = GPIO.input(pumps_ports[gpio_port])
        if GPIO.input(pumps_ports[gpio_port])==0:
            print("Pompa " + gpio_port + " działa")

if args.manual:
    print(is_manual_mode())

if args.on:
    if args.dom:
        pump_on(pumps_ports['dom'])
        print("Pump on")
    elif args.haft:
        pump_on(pumps_ports['haft'])
        print("Pump on")
    elif args.firany:
        pump_on(pumps_ports['firany'])
        print("Pump on")
elif args.off:
    if args.dom:
        pump_off(pumps_ports['dom'])
        print("Pump off")
    elif args.haft:
        pump_off(pumps_ports['haft'])
        print("Pump off")
    elif args.firany:
        pump_off(pumps_ports['firany'])
        print("Pump off")

if args.manual:
    if args.manual and not args.on or not args.off:
        print(is_manual_mode()["manual_mode"])

    if args.manual and args.on and not args.off:
        set_manual_mode(1)

    if args.manual and args.off and not args.on:
        set_manual_mode(0)