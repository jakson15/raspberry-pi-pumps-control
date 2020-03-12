from guizero import App, Box, PushButton, ListBox, Text, CheckBox, TextBox, Window, info
import json
import time
import datetime
import RPi.GPIO as GPIO
from ina219 import INA219
from ina219 import DeviceRangeError

OHMS = 2.4
TEMP = 0.0465

#ina = INA219(shunt_ohms=0.1, max_expected_amps = 0.05, address=0x40)

#ina.configure(voltage_range=ina.RANGE_16V, gain=ina.GAIN_AUTO, bus_adc=ina.ADC_128SAMP, shunt_adc=ina.ADC_128SAMP)


def read():
    voltage = OHMS * ina.current()
    print('Voltage: {0:0.3f}V'.format(ina.shunt_voltage()))
    print ('Current: %.3f mA' % ina.current())
    print('Temperature: {0:0.2f}^C'.format(voltage / TEMP))
    print(str(ina.current()))
    print("Supply Voltage : %.3f V" % ina.supply_voltage())

def pump_off(pin):
    GPIO.output(pin, GPIO.HIGH)

def pump_on(pin):
    GPIO.output(pin, GPIO.LOW)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pumps_ports = {
    'dom': 13,
    'haft': 19,
    'firany': 26,
    'zapas': 6
}

for gpio_port in pumps_ports:
    GPIO.setup(pumps_ports[gpio_port], GPIO.OUT)
    pump_off(pumps_ports[gpio_port])

def do_nothing(a):
    print(a)

def delete_row():
    print(single_line_data)

def open_edition_window(window):
    window.show()

def close_edition_window():
    window_edit_hour.hide()

def safe_data():
    day_data = read_json_data(save_day.value)

    new_data = {
        "start_hour_input":save_day_start_hour_input.value,
        "stop_hour_input":save_day_stop_hour_input.value,
        "pump_1":save_day_pump_1.value,
        "pump_2":save_day_pump_2.value,
        "pump_3":save_day_pump_3.value
    }

    day_data[save_day_row_number.value] = new_data
    file_name = "data_day_" + str(save_day.value) + ".json"
    with open(file_name, "w") as outfile:
        saved_data = json.dump(day_data, outfile, indent=4)

    if (safe_data):
        close_edition_window()

def read_json_data(day):
    file_name = "data_day_" + str(day) + ".json"
    with open(file_name, "r") as json_file:
        data = json.load(json_file)
        return data

def get_current_hour():
    now = int(time.strftime("%H"))
    return now

def schedule_pumps_work():
    day_number = time.strftime("%w")
    day_schedule = read_json_data(day_number)
    working_pumps = []
    for data_key, data_value in day_schedule.items():
        if ( data_value["start_hour_input"] != "" and data_value["stop_hour_input"] != "" and int(data_value["start_hour_input"]) <= get_current_hour() and int(data_value["stop_hour_input"]) > get_current_hour()):
            working_pumps = [data_value["pump_1"], data_value["pump_2"], data_value["pump_3"]]
    return working_pumps

def check_hour_format(text_box):
    if ( isinstance(text_box.value(), int) ):
        print("Poprawna liczba")
        return True
    else:
        app.warn("Błąd", "Podaj godziny w formacie: godz 13:00 (13) tylko cyfra godziny")
        return False

def close_app():
    if app.yesno("Zamknij", "Czy chcesxz zamknąć?"):
        app.destroy()

def data_list_view(day):
    data = read_json_data(day);
    for data_key, data_value in data.items():
        single_line_data = read_working_hours_line(data_value["start_hour_input"], data_value["stop_hour_input"], data_value["pump_1"], data_value["pump_2"], data_value["pump_3"], data_key)
    return day

def auto_manual_turn_off():
    hour = int(time.strftime("%H"))

    if hour == 1:
        #is_manual.value = 0
        return True

def update_pump_status():
    auto_manual_turn_off()
    if 0 == is_manual.value:
        working_pumps = schedule_pumps_work()
        if (working_pumps):
            if (int(working_pumps[0]) == 1 ):
                pump_on(pumps_ports['dom'])
                pump_1_button_status.text = "On"
                pump_1_button_status.text_color = "green"
            else:
                pump_off(pumps_ports['dom'])
                pump_1_button_status.text = "Off"
                pump_1_button_status.text_color = "red"

            if (int(working_pumps[1]) == 1 ):
                pump_on(pumps_ports['haft'])
                pump_2_button_status.text = "On"
                pump_2_button_status.text_color = "green"
            else:
                pump_off(pumps_ports['haft'])
                pump_2_button_status.text = "Off"
                pump_2_button_status.text_color = "red"

            if (int(working_pumps[2]) == 1 ):
                pump_on(pumps_ports['firany'])
                pump_3_button_status.text = "On"
                pump_3_button_status.text_color = "green"
            else:
                pump_off(pumps_ports['firany'])
                pump_3_button_status.text = "Off"
                pump_3_button_status.text_color = "red"
        else:
            pump_1_button_status.text = "Off"
            pump_off(pumps_ports['dom'])
            pump_1_button_status.text_color = "red"
            pump_2_button_status.text = "Off"
            pump_off(pumps_ports['haft'])
            pump_2_button_status.text_color = "red"
            pump_3_button_status.text = "Off"
            pump_off(pumps_ports['firany'])
            pump_3_button_status.text_color = "red"

app = App(title="Sterownie Kotłowni", width="1000", height="500")

window_edit_hour = Window(app, title = "Edycja", height=100, width=450, layout="grid")
Text(window_edit_hour, text="Nr. dnia", width="6", grid=[0,0])
Text(window_edit_hour, text="Nr. rzędu", width="6", grid=[1,0])
Text(window_edit_hour, text="Start", width="4", grid=[2,0])
Text(window_edit_hour, text="", width="4", grid=[3,0])
Text(window_edit_hour, text="Stop", width="4", grid=[4,0])
save_day = TextBox(window_edit_hour, width="6", align="left", grid=[0,1])
save_day_row_number = TextBox(window_edit_hour, width="6", align="left", grid=[1,1])
save_day_start_hour_input = TextBox(window_edit_hour, width="4", grid=[2,1])
Text(window_edit_hour, text=" - ", grid=[3,1])
save_day_stop_hour_input = TextBox(window_edit_hour, width="4", grid=[4,1])
save_day_pump_1 = CheckBox(window_edit_hour, text="Dom", grid=[5,1])
save_day_pump_2 = CheckBox(window_edit_hour, text="Haft", grid=[6,1])
save_day_pump_3 = CheckBox(window_edit_hour, text="Firany", grid=[7,1])
print(save_day.value)

save = PushButton(window_edit_hour, text="Zapisz", width="fill", align="left", command=safe_data, grid=[0,2])
window_edit_hour.hide()

days_box = Box(app, width="fill", align="top")
day_button_1 = PushButton(days_box, text="Poniedziałek", width="fill", align="left", command=data_list_view, args=[1])
day_button_2 = PushButton(days_box, text="Wtorek", width="fill", align="left", command=data_list_view, args=[2])
day_button_3 = PushButton(days_box, text="Środa", width="fill", align="left", command=data_list_view, args=[3])
day_button_4 = PushButton(days_box, text="Czwartek", width="fill", align="left", command=data_list_view, args=[4])
day_button_5 = PushButton(days_box, text="Piątek", width="fill", align="left", command=data_list_view, args=[5])
day_button_6 = PushButton(days_box, text="Sobota", width="fill", align="left", command=data_list_view, args=[6])
day_button_7 = PushButton(days_box, text="Niedziela", width="fill", align="left", command=data_list_view, args=[7])

data_view = Box(app, width="fill", align="top", layout="grid")


working_hours = Box(data_view, align="left", layout="grid", grid=[0,0])

def manual_mode(pump_port):
    if pump_port == pumps_ports['dom']:
        if pump_1_button_status.text == "On":
            pump_off(pumps_ports['dom'])
            pump_1_button_status.text = "Off"
            pump_1_button_status.text_color = "red"
        else:
            pump_on(pumps_ports['dom'])
            pump_1_button_status.text = "On"
            pump_1_button_status.text_color = "green"

    if pump_port == pumps_ports['haft']:
        if pump_2_button_status.text == "On":
            pump_off(pumps_ports['haft'])
            pump_2_button_status.text = "Off"
            pump_2_button_status.text_color = "red"
        else:
            pump_on(pumps_ports['haft'])
            pump_2_button_status.text = "On"
            pump_2_button_status.text_color = "green"

    if pump_port == pumps_ports['firany']:
        if pump_3_button_status.text == "On":
            pump_off(pumps_ports['firany'])
            pump_3_button_status.text = "Off"
            pump_3_button_status.text_color = "red"
        else:
            pump_on(pumps_ports['firany'])
            pump_3_button_status.text = "On"
            pump_3_button_status.text_color = "green"

direct_control = Box(data_view, align="top", layout="grid", grid=[1,0])
Text(direct_control, text="Bezpośrednie sterowanie", size=18, grid=[0,0])
Text(direct_control, text="Dom", size=18, grid=[0,1])
pump_1_button_status = PushButton(direct_control, text="On", width="10", align="left", grid=[1,1], command=manual_mode, args=[pumps_ports['dom']])
Text(direct_control, text="Haft", size=18, grid=[0,2])
pump_2_button_status = PushButton(direct_control, text="On", width="10", align="left", grid=[1,2], command=manual_mode, args=[pumps_ports['haft']])
Text(direct_control, text="Firany", size=18, grid=[0,3])
pump_3_button_status = PushButton(direct_control, text="On", width="10", align="left", grid=[1,3], command=manual_mode, args=[pumps_ports['firany']])
is_manual = CheckBox(direct_control, text="Recznie", align="left", grid=[1,4])

update_pump_status()

Text(working_hours, text="Godziny pracy pomp", size=18, grid=[0,0])

def read_working_hours_line(start_hour, stop_hour, pump_1_value, pump_2_value, pump_3_value, row_number):
    working_hour = Box(working_hours, align="left", layout="grid", grid=[0,row_number])
    Text(working_hour, text=str(row_number) + ".", grid=[0,0])
    start_hour_input = TextBox(working_hour, text=start_hour, width="4", grid=[1,0], enabled=False)
    Text(working_hour, text=" - ", grid=[2,0])
    stop_hour_input = TextBox(working_hour, text=stop_hour, width="4", grid=[3,0], enabled=False)
    pump_1 = CheckBox(working_hour, text="Dom", grid=[4,0], enabled=False)
    pump_2 = CheckBox(working_hour, text="Haft", grid=[5,0], enabled=False)
    pump_3 = CheckBox(working_hour, text="Firany", grid=[6,0], enabled=False)

    if (bool(pump_1_value)):
        pump_1.value = pump_1_value

    if (bool(pump_2_value)):
        pump_2.value = pump_2_value

    if (bool(pump_3_value)):
        pump_3.value = pump_3_value

    return True

data_list_view(time.strftime("%w"))

app.repeat(10000, update_pump_status)

buttons = Box(app, width="fill", align="bottom")
PushButton(buttons, text="Edytuj", width="fill", align="right", command=open_edition_window, args=[window_edit_hour])
PushButton(buttons, text="Zamknij", width="fill", align="left", command=close_app)

app.display()
