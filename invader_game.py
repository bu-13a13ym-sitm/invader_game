import argparse
import asyncio
from gpiozero import Button, LED
from spidev import SpiDev
from time import sleep
from random import randint as rd
from sys import stdout
from threading import Thread
from global_variables import field_width, refresh_rate, fps, player_graphic, boss_graphic, easy, nomal, hard
from field import Field, print_field
from bullet import BulMap
from entity import Entity


#GPIO settings
segments = {
    'A': LED(18),
    'B': LED(23),
    'C': LED(24),
    'D': LED(25),
    'E': LED(12),
    'F': LED(16),
    'G': LED(20)
}

char_to_segments = {
    '0': ['A', 'B', 'C', 'D', 'E', 'F'],
    '1': ['B', 'C'],
    '2': ['A', 'B', 'D', 'E', 'G'],
    '3': ['A', 'B', 'C', 'D', 'G'],
    '4': ['B', 'C', 'F', 'G'],
    '5': ['A', 'C', 'D', 'F', 'G'],
    '6': ['A', 'C', 'D', 'E', 'F', 'G'],
    '7': ['A', 'B', 'C'],
    '8': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    '9': ['A', 'B', 'C', 'D', 'F', 'G'],
    '10': ['G'],
    'A': ['A', 'D'],
    'B': ['B', 'E'],
    'C': ['C', 'F'],
    'X': ['B', 'C', 'E', 'F', 'G'],
    'a': ['A'],
    'b': ['B'],
    'c': ['C'],
    'd': ['D'],
    'e': ['E'],
    'f': ['F'],
    'N': []
}

def display(char):
    for segment in segments.values():
        segment.off()
    for segment in char_to_segments[char]:
        segments[segment].on()

def read_adc(channel):
    if channel < 0 or channel > 7:
        return -1
    command = [1, (8 + channel) << 4, 0]
    response = spi.xfer2(command)
    adc_out = ((response[1] & 3) << 8) + response[2]
    return adc_out

def scale_value(value):
    return value * field_width // 4095

def pressed(frame, bul_map):
    player.fire(frame, input=0, bul_map=bul_map)

def reload_indicater(player):
    circle = ['a', 'b', 'c', 'd', 'e', 'f']
    recode = []
    for segment in char_to_segments[circle]:
        recode.append(segment)
        for char in recode:
            display(char)
            sleep((player.reload // fps) / len(circle))

def detect_reload(player, clear, reload_indicater):
    global reloading
    reloading = True
    while not clear:
        if player.reloading:
            reload_thread = Thread(target=reload_indicater, args=player)
            reload_thread.start()
            reload_thread.join()
    sleep(0.2)
    reloading = False

spi = SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000
channel = 0
button = Button(17)
button.when_pressed = lambda: pressed(frame, bul_map)


#choose game level from command line
parser = argparse.ArgumentParser(description="")
parser.add_argument("--level", type=str, default= "nomal", help="choose game level from easy, nomal, and hard")
args = parser.parse_args()
level = args.level.lower()
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
        level = input("choose game level from easy, nomal, and hard: ").lower()

bhp, bvel, bbul_vel, brapid_fire, breload, bstart, php, pvel, pbul_vel, prapid_fire, preload = mode.values()


#initialize new game
player = Entity(hp=php, width=len(player_graphic), pos=rd(1,23), vel=pvel, bul_dam=1, bul_vel=pbul_vel, burst=True, rapid_fire=prapid_fire, reload=preload)
boss = Entity(hp=bhp, width=len(boss_graphic), pos=rd(2, 22), vel=bvel, bul_dam=1, bul_vel=bbul_vel, burst=False, rapid_fire=brapid_fire, reload=breload)
clear = 0
reloading = False
try:
    frame = 0
    bul_map = BulMap()
    field = Field(player=player, boss=boss, bul_map=bul_map)
    for col in field.field:
        print(col)
        sleep(0.3)
    frame += 1
    reload_thread = Thread(target=detect_reload, args=(player, clear, reload_indicater))
    reload_thread.start()
    pre_php = 10000

    #main game start
    while not clear:
        sleep(refresh_rate)
        bul_map.advance_frame(boss=boss, player=player, frame=frame)
        adc = read_adc(channel)
        player.change_pos(scale_value(adc), frame)
        boss.change_pos(rd(2,22), frame)
        if frame > bstart * fps:
            boss.fire(frame, input=rd(0,15), bul_map=bul_map)
        player.fire(frame, input=1, bul_map=bul_map)
        field = Field(player=player, boss=boss, bul_map=bul_map)
        print_field(field)
        stdout.flush()
        if (not reloading) and (pre_php != player.hp):
            display(player.hp)
        frame += 1
        pre_php = player.hp
        if boss.hp == 0:
            clear = 1
            break
        elif player.hp == 0:
            clear = -1
            break
    
    #game ending process
    reload_thread.join()
    if clear > 0:
        for col, s_col in enumerate(field.field):
            for row, s_row in enumerate(s_col):
                if s_row == " ":
                    field.field[col] = s_col[:row] + "□" + s_col[row + 1:]
                    s_col = field.field[col]
        print_field(field)
        sleep(0.5)

        async def command_line(field):
            message = "!YOU WIN!"
            message_begin = len(field.field[0]) // 2 - len(message) // 2
            for col, f_col in enumerate(reversed(field.field)):
                for row, f_row in enumerate(f_col):
                    if col == len(field.field) // 2 and row > message_begin and row <= message_begin + len(message):
                        field.field[len(field.field) - col - 1] = f_col[:row] + message[row - message_begin - 1] + f_col[row + 1:]
                    else:
                        field.field[len(field.field) - col - 1] = f_col[:row] + " " + f_col[row + 1:]
                    f_col = field.field[len(field.field) - col - 1]
                    print_field(field)
                    await asyncio.sleep(1/150)

        async def led():
            count = 0
            circle = ('A', 'B', 'C')
            while True:
                display(circle[count % len(circle)])
                count += 1
                await asyncio.sleep(1 / 30)
        
        async def main(field):
            command_line_future = asyncio.create_task(command_line(field))
            led_future = asyncio.create_task(led())
            
            await command_line_future
            led_future.cancel()
            try:
                await led_future
            except asyncio.CancelledError:
                pass
        
        asyncio.run(main(field))

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

        async def command_line(field):
            message = "YOU LOSE..."
            message_begin = len(field.field[0]) // 2 - len(message) // 2
            for count, col in enumerate(reversed(field.field)):
                del_list = [True for row in col]
                while any(del_list):
                    del_field = rd(0, len(col) - 1)
                    while field.field[len(field.field) - count - 1] and not del_list[del_field]:
                        del_field = rd(0, len(col) - 1)
                    if count == len(field.field) // 2 and del_field > message_begin and del_field <= message_begin + len(message):
                        field.field[len(field.field) - count - 1] = col[:del_field] + message[del_field - message_begin - 1] + col[del_field + 1:]
                    else:
                        field.field[len(field.field) - count - 1] = col[:del_field] + " " + col[del_field + 1:]
                    del_list[del_field] = False
                    col = field.field[len(field.field) - count - 1]
                    print_field(field)
                    await asyncio.sleep(1/150)

        async def led():
            count = 0
            X = ('X', 'N')
            while True:
                display(X[count % len(X)])
                count += 1
                await asyncio.sleep(0.5)

        async def main(field):
            command_line_future = asyncio.create_task(command_line(field))
            led_future = asyncio.create_task(led())

            await command_line_future
            led_future.cancel()

            try:
                await led_future
            except asyncio.CancelledError:
                pass
        
        asyncio.run(main(field))

except KeyboardInterrupt:
    print("The game was interrupted.")
    pass

finally:
    for segment in segments.values():
        segment.off()