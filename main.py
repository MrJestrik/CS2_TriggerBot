# Made by im-razvan - CS2 TriggerBot W/O Memory Writing
import pymem, pymem.process, time, win32api, win32con
from random import uniform

# https://github.com/a2x/cs2-dumper/
dwEntityList = 0x17ADAE0
dwLocalPlayerPawn = 0x16B9388
m_iIDEntIndex = 0x153C
m_iTeamNum = 0x3BF
m_iHealth = 0x32C

dwForceJump = 0x16B2820
m_fFlags = 0x3C8

width = win32api.GetSystemMetrics(0)
height = win32api.GetSystemMetrics(1)
midWidth = int((width + 1) / 2)
midHeight = int((height + 1) / 2)

def main():
    print("TriggerBot started.")
    pm = pymem.Pymem("cs2.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

    state_left = win32api.GetKeyState(0x05)  # Left button up = 0 or 1. Button down = -127 or -128

    toggled = False

    while True:
        try:
            a = win32api.GetKeyState(0x05)
            if a != state_left:  # Button state changed
                state_left = a
                # print(a)
                if a < 0:toggled=True
                else:toggled=False
            # if keyboard.is_pressed("x"):
            if toggled:
                player = pm.read_longlong(client + dwLocalPlayerPawn)
                entityId = pm.read_int(player + m_iIDEntIndex)

                if entityId > 0:
                    entList = pm.read_longlong(client + dwEntityList)

                    entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))

                    entityTeam = pm.read_int(entity + m_iTeamNum)
                    entityHp = pm.read_int(entity + m_iHealth)

                    playerTeam = pm.read_int(player + m_iTeamNum)

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

if __name__ == '__main__':
    main()
