
import json
import time
import threading
from statistics import median
from tkinter import *
from tkinter import ttk
import requests
from tkinter import messagebox


# ##################################################################
# #######   SETUP   ########
# ##################################################################


# WATER TANK SPECS
TANK_EMPTY_DIST = 350  # Calibrate water tank empty distance value.
TANK_FULL_DIST = 20  # Calibrate water tank full distance value.
# Calculate difference between full and empty distance.
TANK_CAP_DIST = TANK_EMPTY_DIST - TANK_FULL_DIST


# HTTP REQUEST URL'S
# URL for cm variable in particle cloud. Used in GET request.
CM_URL = "https://api.particle.io/v1/devices/e00fce68a9199af5dde8f554/cm?access_token=1a632432fee687185b856df980e76f649a3e8e13"
# URL for valve_status variable in particle cloud. Used in GET request.
VALVE_URL = "https://api.particle.io/v1/devices/e00fce68a9199af5dde8f554/valve_status?access_token=1a632432fee687185b856df980e76f649a3e8e13"
# URL for command_word function in particle cloud. Used in POST request.
COMMAND_URL = "https://api.particle.io/v1/devices/e00fce68a9199af5dde8f554/control_word"


#  UPDATE FREQUENCIES
# UPDATE_DISPLAY_FREQUENCY = 30  # in milli seconds
UPDATE_PERCENT_FREQUENCY = 30  # in seconds
# UPDATE_VALVE_STATUS_FREQUENCY = 30  # in seconds
UPDATE_COMMAND_FREQUENCY = 1  # in seconds


#  GLOBALS FOR WATER LEVEL AND CONTROL
# number of values to collect in a list before calculating the median. To help with sensor accuracy.
WATER_LIST_SIZE = 5
auto_flag = False  # Init Global variable. Is auto mode active?
water_value_perc = 0  # Init Global variable. Percentage water tank filled.
# Init Global variable (man off = 10, man on = 11, auto on = 1, auto off = 0)
valve_status = 10
# Init Global Variable. Valve command codes. (Man off = 120, Man on = 110, Auto on = 0 -30, Auto off = 31 - 100)
valve_command = 120
temp_command = 120


# ##################################################################
# #######   FUNCTION DEFINITIONS   ########
# ##################################################################

def tank_percent():  # DETERMINES HOW FULL THE WATER TANK IS AS A %
    # Fetches the distance to water.Particle Cloud API call GET request. Creates list of WATER_LIST_SIZE length with each value converted to an integer.
    list_water_values = populate_list()
    # Calculates median from list to reduce erroneous signals from ultrasonic sensor.
    median_water_value = median(list_water_values)
    # uses median value to calculate how full the water tank is as a %.
    water_value_perc = percent(median_water_value, TANK_CAP_DIST)
    return water_value_perc


def populate_list():  # CREATE A LIST OF VALUES FROM THE ULTRASONIC SENSOR
    water_list = []  # create empty list
    i = 1
    while i < (WATER_LIST_SIZE + 1):
        # HTTP GET request, response object returned
        response = requests.request("GET", CM_URL)
        response_dict = json.loads(
            response.text.encode('utf8'))  # convert to a dict
        # assign only result value from dict and convert value to a integer.
        response_value = int(response_dict.get('result'))
        # add value to the list of water values
        water_list.append(response_value)
        i += 1
    print(str(water_list))
    return water_list


def percent(num_value, num_total):  # CALCULATES % GIVEN A VALUE AND THE TOTAL.
    if num_value == -1:  # if the ultrasonic sensor gets a reading for cm less than its minumum it returns -1 as the distance in cm
        perc = 100  # if the water level is past or at the water tanks capacity force the percentage value  = 100
        return perc
    if num_value == -2:   # if the ultrasonic sensor gets a reading for cm more than its maximum it returns -2 as the distance in cm
        perc = 0  # if the water level is at or below the water tanks empty condition force the percentage value  = 0
        return perc
    else:
        # Use the median water value to calculate the water level as a %
        perc = int(((num_total - (num_value - 20)) / num_total) * 100)
        return perc


def send_command(command):  # SENDS THE COMMAND CODE PASSED IN AND UPDATES VALVE STATUS
    global valve_status  # Use global variable
    # Payload command and access token for access to Particle cloud
    payload = {'arg': str(
        command), 'access_token': '1a632432fee687185b856df980e76f649a3e8e13'}
    # HTTP POST request. Sends command code (Man off = 120, Man on = 110, Auto on = 0 -30, Auto off = 31 - 100) to activate water valve. Return value is valve_status code. (man off = 10, man on = 11, auto on = 1, auto off = 0)
    valve_status = requests.request("POST", COMMAND_URL, data=payload)


def check_valve():
    global valve_status
    global valve_command
    while valve_status == 10:
        if valve_command == 120:
            break
        else:
            messagebox.showerror(
                "Error", "Water Valve status is incorrect. Please restart Application")
    while valve_status == 11:
        if valve_command == 110:
            break
        else:
            messagebox.showerror(
                "Error", "Water Valve status is incorrect. Please restart Application")
    while valve_status == 0:
        if (valve_command > 30 and valve_command <= 100):
            break
        else:
            messagebox.showerror(
                "Error", "Water Valve status is incorrect. Please restart Application")
    while valve_status == 1:
        if (valve_command <= 30 and valve_command >= 0):
            break
        else:
            messagebox.showerror(
                "Error", "Water Valve status is incorrect. Please restart Application")


def refresh_buttons(percent):
    if (percent >= 0) and (percent <= 30):
        auto_green()
    else:
        auto_red()


def update_progress(percent):  # UPDATES THE BAR GRAPH AND % LABEL WITH THE PERCENT VALUE
    # updates bar graph value from percent value
    progress_bar["value"] = percent
    progress_bar.update()  # updates the bar graph on screen
    percent_label.config(text=str(percent) + '%')  # update percent value label


def auto_green():  # SET AUTO BUTTON BACKGROUND COLOUR TO GREEN AND RESETS OTHERS
    auto_button['bg'] = "green"
    on_button['bg'] = "#DADAC4"
    off_button['bg'] = "#DADAC4"
    auto_button.config(activebackground="green")
    off_button.config(activebackground="#DADAC4")
    on_button.config(activebackground="#DADAC4")


def auto_red():   # SET AUTO BUTTON BACKGROUND COLOUR TO RED AND RESETS OTHERS
    auto_button['bg'] = "red"
    on_button['bg'] = "#DADAC4"
    off_button['bg'] = "#DADAC4"
    auto_button.config(activebackground="red")
    off_button.config(activebackground="#DADAC4")
    on_button.config(activebackground="#DADAC4")


def manual_on_green():   # SET ON BUTTON BACKGROUND COLOUR TO GREEN AND RESETS OTHERS
    auto_button['bg'] = "#DADAC4"
    on_button['bg'] = "green"
    off_button['bg'] = "#DADAC4"
    on_button.config(activebackground="green")
    off_button.config(activebackground="#DADAC4")
    auto_button.config(activebackground="#DADAC4")


def manual_off_red():   # SET OFF BUTTON BACKGROUND COLOUR TO RED AND RESETS OTHERS
    auto_button['bg'] = "#DADAC4"
    on_button['bg'] = "#DADAC4"
    off_button['bg'] = "red"
    on_button.config(activebackground="#DADAC4")
    off_button.config(activebackground="red")
    auto_button.config(activebackground="#DADAC4")


def auto_mode(percent):  # WHEN AUTO BUTTON ACTIVATED THIS USES THE CURRENT PERCENT VALUE TO STORE A COMMAND CODE AND UPDATE THE BUTTON COLOUR
    global auto_flag  # Use global variable
    global valve_command   # Use global variable
    global temp_command
    auto_flag = True  # auto mode activated
    # If  30% or less store percent value as command code and change button colour to Green
    if (percent >= 0) and (percent <= 30) and auto_flag:
        valve_command = percent
        #temp_command = valve_command
        auto_green()
    else:   # If above 30% store percent value as command code and change button colour to Red
        valve_command = percent
        #temp_command = valve_command
        auto_red()


def valve_command_on():  # WHEN ON BUTTON ACTIVATED THIS INVERTS THE AUTO FLAG, SETS THE MANUAL ON COMMAND CODE AND UPDATES THE BUTTON COLOUR
    global valve_command  # Use global variable
    global auto_flag  # Use global variable
    auto_flag = False  # auto mode deactivated
    manual_on_green()
    valve_command = 110  # store manual on command code
    send_command(valve_command)
    #temp_command = valve_command


def valve_command_off():  # WHEN OFF BUTTON ACTIVATED THIS INVERTS THE AUTO FLAG, SETS THE MANUAL OFF COMMAND CODE AND UPDATES THE BUTTON COLOUR
    global valve_command  # Use global variable
    global auto_flag  # Use global variable
    auto_flag = False  # auto mode deactivated
    manual_off_red()
    valve_command = 120  # store manual off command code
    send_command(valve_command)
    #temp_command = valve_command


def auto_mode_refresh(percent):
    global auto_flag  # Use global variable
    global valve_command   # Use global variable
    if (percent >= 0) and (percent <= 30) and auto_flag:
        valve_command = percent
        auto_green()
    if (percent > 30) and (percent <= 100) and auto_flag:   # If above 30% store percent value as command code and change button colour to Red
        valve_command = percent
        auto_red()

def command_refresh(command):
    global temp_command
    if (temp_command != command):
        send_command(command)
        #time.sleep(UPDATE_COMMAND_FREQUENCY)
        check_valve()
        
    
def close():
    win.destroy()


def thread1():
    global water_value_perc
    global temp_command
    global valve_command
    temp_command = valve_command
    water_value_perc = tank_percent()
    update_progress(water_value_perc)
    auto_mode_refresh(water_value_perc)
    win.after(UPDATE_PERCENT_FREQUENCY * 1000, thread1)


def thread2():
    global valve_command
    command_refresh(valve_command)
    win.after(UPDATE_COMMAND_FREQUENCY * 1000, thread2)


# ##################################################################
# #######   GUI DEFINITIONS   ########
# ##################################################################

win = Tk()  # Creates the main window and frame with a black border.
win.title("Tank-Sense Smart Controller")
win.geometry("470x255")
win.config(bg="#000000", bd=5)
main_frame = Frame(win, bg="#ffffff", height=307, width=460)


# ##################################################################
# #######   WIDGET DEFINITIONS   ########
# ##################################################################


gui_title_label = Label(main_frame, text='Tank-Sense Smart Controller',
                        font="helvetica 14 bold underline", bg="#ffffff")  # Create all the widgets.
progress_label = Label(main_frame, text='Water Tank \n Capacity',
                       font="helvetica 12 bold", bg="#ffffff", bd=4)
percent_label = Label(main_frame, text='   %', bg="#ffffff",
                      font="helvetica 16 bold", bd=4)
auto_button = Button(main_frame, text='AUTO', font="helvetica 12 bold",
                     bg="#DADAC4", width=8, height=2, command=lambda: auto_mode(water_value_perc))
on_button = Button(main_frame, text='ON', font="helvetica 12 bold",
                   bg="#DADAC4", width=8, height=2, command=valve_command_on)
off_button = Button(main_frame, text='OFF', font="helvetica 12 bold",
                    bg="#DADAC4", width=8, height=2, command=valve_command_off)
progress_bar = ttk.Progressbar(
    main_frame, orient=VERTICAL, length=150, mode='determinate', maximum=100, value=0)
error_label = Label(main_frame, text='ERROR \n Please close the window \n & restart',
                    font="helvetica 14 bold", bg="#ffffff")


# ##################################################################
# #######   DRAW GUI + WIDGETS   ########
# ##################################################################


main_frame.grid(row=0, column=0)
gui_title_label.grid(row=0, column=0, columnspan=2, ipadx=104)
progress_label.grid(row=1, column=0, rowspan=2, ipady=5)
percent_label.grid(row=1, column=1, pady=2)
progress_bar.grid(row=2, column=1, rowspan=4, ipadx=40, pady=8, ipady=8)
auto_button.grid(row=3, column=0)
on_button.grid(row=4, column=0)
off_button.grid(row=5, column=0)


# ##################################################################
# #######   MAIN LOOP   ########
# ##################################################################


manual_off_red()
valve_command_off()
send_command(valve_command)

try:
    t1 = threading.Thread(target=thread1)  # create thread 1
    t2 = threading.Thread(target=thread2)  # create thread 2

    t1.start()  # start thread 1
    t2.start()  # start thread 2

    win.protocol("WM_DELETE_WINDOW", close)  # close window
    win.mainloop()  # how tk can do work without freezing up the UI
except:
    messagebox.showerror(
        "Error", "Please close window and restart application")

    win.protocol("WM_DELETE_WINDOW", close)  # close window
