import pymem.process, time, win32api, win32con, os
from random import uniform
from pynput import mouse
import keyboard

# https://github.com/a2x/cs2-dumper/
dwEntityList = 0x17ADAF0
dwLocalPlayerPawn = 0x16B9388
m_iIDEntIndex = 0x153C
m_iTeamNum = 0x3BF
m_iHealth = 0x32C

dwForceJump = 0x16B2810
m_fFlags = 0x3C8

width = win32api.GetSystemMetrics(0)
height = win32api.GetSystemMetrics(1)
midWidth = int((width + 1) / 2)
midHeight = int((height + 1) / 2)

# Global variables to store button and virtual key code
last_click_button = mouse.Button.middle
last_click_virtual_key = 0x03

# Counter to keep track of the number of clicks
click_press_count = 0

mouse_listener = None

mouse_bind = True

def on_key_event(event):
    global click_press_count, last_click_button, last_click_virtual_key, mouse_bind
    def get_virtual_key(key):
        try:
            virtual_key = keyboard.key_to_scan_codes(key)[0]
            return virtual_key
        except IndexError:
            print(f"Error: Virtual key not found for {key}")
            return None
    if event.event_type == "down":
        click_press_count += 1
        last_click_button = event.name
        last_click_virtual_key = get_virtual_key(last_click_button)
        if click_press_count >= 1:
            mouse_bind = False
            stop_listening()

def on_click(x, y, button, pressed):
    global last_click_button, last_click_virtual_key, click_press_count, mouse_bind

    if pressed:
        click_press_count += 1
        last_click_button = button
        if button.value == (4, 2, 0):
            last_click_virtual_key = 0x01
        elif button.value == (16, 8, 0):
            last_click_virtual_key = 0x02
        elif button.value == (64, 32, 0):
            last_click_virtual_key = 0x04
        elif button.value == (256, 128, 1):
            last_click_virtual_key = 0x05
        elif button.value == (256, 128, 2):
            last_click_virtual_key = 0x06

        # Check if the maximum number of clicks is reached
        if click_press_count >= 1:
            mouse_bind = True
            stop_listening()

# Function to stop the mouse listener
def stop_listening():
    global mouse_listener
    print("Stopping mouse listener.")
    mouse_listener.stop()
    keyboard.unhook_all()
    print(last_click_button, last_click_virtual_key)
    #mouse_listener.join()

def change_key_bind():
    global mouse_listener
    # Start listening for mouse clicks
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    keyboard.hook(on_key_event)

    while mouse_listener.is_alive():
        pass

    keyboard.unhook_all()

# Access last click information after the script has run
# print(f"Button Clicked: {last_click_button}")
# print(f"Button VKey: {last_click_virtual_key}")

game_handle = pymem.Pymem("cs2.exe")
client_dll = pymem.process.module_from_name(game_handle.process_handle, "client.dll").lpBaseOfDll
state = win32api.GetKeyState(last_click_virtual_key)  # Left button up = 0 or 1. Button down = -127 or -128
toggled = False

while True:
    try:
        if keyboard.is_pressed("insert"):
            change_key_bind()
        if mouse_bind:
            a = win32api.GetKeyState(last_click_virtual_key)
            if a != state:  # Button state changed
                state_left = a
                # print(a)
                if a < 0:toggled=True
                else:toggled=False
            if toggled:
                player = game_handle.read_longlong(client_dll + dwLocalPlayerPawn)
                entityId = game_handle.read_int(player + m_iIDEntIndex)

                if entityId > 0:
                    entList = game_handle.read_longlong(client_dll + dwEntityList)

                    entEntry = game_handle.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = game_handle.read_longlong(entEntry + 120 * (entityId & 0x1FF))

                    entityTeam = game_handle.read_int(entity + m_iTeamNum)
                    entityHp = game_handle.read_int(entity + m_iHealth)

                    playerTeam = game_handle.read_int(player + m_iTeamNum)

                    if entityTeam != playerTeam and entityHp > 0:
                        time.sleep(uniform(0.01, 0.05))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                        time.sleep(0.1)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

                    time.sleep(0.03)
        else:
            if keyboard.is_pressed(last_click_button):
                toggled = True
            else:
                toggled = False
            if toggled:
                player = game_handle.read_longlong(client_dll + dwLocalPlayerPawn)
                entityId = game_handle.read_int(player + m_iIDEntIndex)

                if entityId > 0:
                    entList = game_handle.read_longlong(client_dll + dwEntityList)

                    entEntry = game_handle.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = game_handle.read_longlong(entEntry + 120 * (entityId & 0x1FF))

                    entityTeam = game_handle.read_int(entity + m_iTeamNum)
                    entityHp = game_handle.read_int(entity + m_iHealth)

                    playerTeam = game_handle.read_int(player + m_iTeamNum)

                    if entityTeam != playerTeam and entityHp > 0:
                        time.sleep(uniform(0.01, 0.05))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                        time.sleep(0.1)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

                    time.sleep(0.03)
        time.sleep(0.002)

    except KeyboardInterrupt:
        break
    except:
        pass
