import argparse
from time import sleep
from random import randint as rd
from sys import stdout
from pynput import keyboard
from threading import Thread
from global_variables import field_height, field_width, refresh_rate, fps, max_items, player_graphic, enemy_graphic, item_graphic, easy, nomal, hard, effects
from field2_0 import Field
from maps import ItemMap, BulMap
from entities import Creature, Item


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

ehp, evel, ebul_vel, erapid_fire, ereload, estart, php, pvel, pbul_vel, prapid_fire, preload = mode.values()


#initialize game
frame = 0
player = Creature(hp=php,
                width=len(player_graphic),
                pos=rd(1,23),
                vel=pvel,
                bul_dam=1,
                bul_vel=pbul_vel,
                burst=True,
                rapid_fire=prapid_fire,
                reload=preload)
enemy = Creature(hp=ehp,
               width=len(enemy_graphic),
               pos=rd(2, 22),
               vel=evel,
               bul_dam=1,
               bul_vel=ebul_vel,
               burst=False,
               rapid_fire=erapid_fire,
               reload=ereload)
bul_map = BulMap()
item_map = ItemMap()
field = Field(player=player, enemy=enemy, item_map=item_map, bul_map=bul_map)
item_list = []
for col in field.field:
    print(col)
    sleep(0.2)
frame += 1


#player action settings
def on_press(key):
    try:
        if hasattr(key, "char") and key.char == "a":
            player.change_pos(new_pos=(player.pos["x"] - 1), frame=frame)
        elif hasattr(key, "char") and key.char == "d":
            player.change_pos(new_pos=(player.pos["x"] + 1), frame=frame)
        elif key == keyboard.Key.enter:
            player.fire(frame, input=0, bul_map=bul_map)
        elif key == keyboard.Key.esc:
            return False
    except AttributeError:
        pass
def start_listener(listener):
    listener.start()
    listener.join()
def stop_listener(listener):
    listener.stop()

listener = keyboard.Listener(on_press=on_press)
listener_thread = Thread(target=start_listener, args=(listener,))
listener_thread.start()


clear = 0
try:
    #main game start
    while not clear:
        sleep(refresh_rate)
        if (len(item_list) < max_items) and not rd(0, 1 * fps):
            item_list.append(Item(width=len(item_graphic),
                                  pos=(rd(2, field_width - 3), rd(3, field_height - 3)),
                                  effect=list(effects.keys())[rd(0, len(effects) - 1)],
                                  player=player,
                                  enemy=enemy,
                                  item_map=item_map,
                                  bul_map=bul_map,
                                  item_list=item_list))
        bul_map.advance_frame(frame)
        enemy.change_pos(rd(2,22), frame)
        if frame > estart * fps:
            enemy.fire(frame, input=rd(0,15), bul_map=bul_map)
        player.fire(frame, input=1, bul_map=bul_map)
        field = Field(player=player, enemy=enemy, item_map=item_map, bul_map=bul_map)
        field.print_field()
        stdout.flush()
        frame += 1
        if enemy.hp == 0:
            clear = 1
            break
        elif player.hp == 0:
            clear = -1
            break

    #game ending process
    for item in item_list:
        item.sustain = 0
        item.hp = 0
    if clear > 0:
        for col, s_col in enumerate(field.field):
            for row, s_row in enumerate(s_col):
                if s_row == " ":
                    field.field[col] = s_col[:row] + "□" + s_col[row + 1:]
                    s_col = field.field[col]
        field.print_field()
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
                field.print_field()
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
        field.print_field()
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
                field.print_field()
                sleep(1/300)
except KeyboardInterrupt:
    pass
finally:
    stop_listener(listener)
    listener_thread.join()