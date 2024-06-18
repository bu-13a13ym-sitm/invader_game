import argparse
from time import sleep
from random import randint as rd
from sys import stdout
from pynput import keyboard
from threading import Thread
from global_variables import refresh_rate, fps, player_graphic, boss_graphic, easy, nomal, hard
from field import Field, print_field
from bullet import BulMap
from entity import Entity


#choose game level from command line
parser = argparse.ArgumentParser(description="")
parser.add_argument("--level", type=str,help="choose game level from easy, nomal, and hard")
args = parser.parse_args()
level = args.level
if type(level) == str:
    level.lower()
while True:
    if level == "easy":
        mode = easy
        break
    elif level == "nomal":
        mode = nomal
        break
    elif level == "hard":
        mode = hard
        break
    else:
        level = input('choose game level from "easy", "nomal", and "hard": ').lower()

bhp, bvel, bbul_vel, brapid_fire, breload, bstart, php, pvel, pbul_vel, prapid_fire, preload = mode.values()


#initialize game
frame = 0
player = Entity(hp=php, width=len(player_graphic), pos=rd(1,23), vel=pvel, bul_dam=1, bul_vel=pbul_vel, burst=True, rapid_fire=prapid_fire, reload=preload)
boss = Entity(hp=bhp, width=len(boss_graphic), pos=rd(2, 22), vel=bvel, bul_dam=1, bul_vel=bbul_vel, burst=False, rapid_fire=brapid_fire, reload=breload)
bul_map = BulMap()
field = Field(player=player, boss=boss, bul_map=bul_map)
for col in field.field:
    print(col)
    sleep(0.2)
frame += 1


#player action settings
def on_press(key):
    try:
        if hasattr(key, "char") and key.char == "a":
            player.change_pos(new_pos=(player.pos - 1), frame=frame)
        elif hasattr(key, "char") and key.char == "d":
            player.change_pos(new_pos=(player.pos + 1), frame=frame)
        elif key == keyboard.Key.enter:
            player.fire(frame, input=0, bul_map=bul_map)
        elif key == keyboard.Key.esc:
            return False
    except AttributeError:
        pass
def start_listener():
    global listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()
def stop_listner():
    global listener
    if listener:
        listener.stop()
        listener.join()

listener_thread = Thread(target=start_listener)
listener_thread.start()


clear = 0
try:
    #main game start
    while not clear:
        sleep(refresh_rate)
        bul_map.advance_frame(boss=boss, player=player, frame=frame)
        boss.change_pos(rd(2,22), frame)
        if frame > bstart * fps:
            boss.fire(frame, input=rd(0,15), bul_map=bul_map)
        player.fire(frame, input=1, bul_map=bul_map)
        field = Field(player=player, boss=boss, bul_map=bul_map)
        print_field(field)
        stdout.flush()
        frame += 1
        if boss.hp == 0:
            clear = 1
            break
        elif player.hp == 0:
            clear = -1
            break

    #game ending process
    if clear > 0:
        for col, s_col in enumerate(field.field):
            for row, s_row in enumerate(s_col):
                if s_row == " ":
                    field.field[col] = s_col[:row] + "□" + s_col[row + 1:]
                    s_col = field.field[col]
        print_field(field)
        sleep(0.5)
        message = "!YOU WIN!"
        message_begin = len(field.field[0]) // 2 - len(message) // 2
        for col, f_col in enumerate(field.field):
            for row, f_row in enumerate(f_col):
                if col == len(field.field) // 2 and row > message_begin and row <= message_begin + len(message):
                    field.field[col] = f_col[:row] + message[row - message_begin - 1] + f_col[row + 1:]
                else:
                    field.field[col] = f_col[:row] + " " + f_col[row + 1:]
                f_col = field.field[col]
                print_field(field)
                sleep(1/500)
    elif clear < 0:
        for col, s_col in enumerate(field.field):
            for row, s_row in enumerate(s_col):
                if s_row == " ":
                    field.field[col] = s_col[:row] + "■" + s_col[row + 1:]
                    s_col = field.field[col]
                elif s_row == "■":
                    field.field[col] = s_col[:row] + "□" + s_col[row + 1:]
                    s_col = field.field[col]
        print_field(field)
        sleep(0.5)
        message = "YOU LOSE..."
        message_begin = len(field.field[0]) // 2 - len(message) // 2
        for count, col in enumerate(reversed(field.field)):
            del_list = [True for row in col]
            while any(del_list):
                del_field = rd(0, len(col) - 1)
                while field.field[len(field.field) - count - 1] and not del_list[del_field]:
                    del_field = rd(0, len(col) - 1)
                field.field[len(field.field) - count - 1] = col[:del_field] + " " + col[del_field + 1:]
                if count == len(field.field) // 2 and del_field > message_begin and del_field <= message_begin + len(message):
                    field.field[len(field.field) - count - 1] = col[:del_field] + message[del_field - message_begin - 1] + col[del_field + 1:]
                del_list[del_field] = False
                col = field.field[len(field.field) - count - 1]
                print_field(field)
                sleep(1/300)
except KeyboardInterrupt:
    pass
finally:
    stop_listner()