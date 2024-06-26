from global_variables import field_width, field_height, refresh_rate, player_graphic, enemy_graphic, bul_graphic, fast_bul_graphic, fastest_bul_graphic
from bullet import BulMap
from entity import Entity
from random import randint as rd
from sys import stdout
from time import sleep


class Field:
    def __init__(self,*, enemy=Entity(), player=Entity(), bul_map=BulMap()):
        self.field = []
        self.field.append("-" * (field_width + 2))
        for b in enemy_graphic:
            text = "|" + " " * (enemy.pos - (len(b) // 2)) + b
            text += " " * (field_width - (len(text) - 1)) + "|"
            self.field.append(text)
        for blank in range(field_height - len(enemy_graphic) - len(player_graphic)):
            self.field.append("|" + " " * field_width + "|")
        for p in player_graphic:
            text = "|" + " " * (player.pos - (len(p) // 2)) + p
            text += " " * (field_width - (len(text) - 1)) + "|"
            self.field.append(text)
        self.field.append("-" * (field_width + 2))
        for col, b_col in enumerate(bul_map.map):
            curr_col = self.field[col + 1]
            for row, b_row in enumerate(b_col):
                if b_row["owner"]:
                    if self.field[col + 1][row] == " ":
                        vel = abs(b_row["vel"])
                        if vel <= 16:
                            self.field[col + 1] = curr_col[:row + 1] + bul_graphic + curr_col[row + 2:]
                        elif vel <= 32:
                            self.field[col + 1] = curr_col[:row + 1] + fast_bul_graphic + curr_col[row + 2:]
                        else:
                            self.field[col + 1] = curr_col[:row + 1] + fastest_bul_graphic + curr_col[row + 2:]
                    elif col < len(enemy_graphic):
                        enemy.get_dam(dam=bul_map.map[col][row]["dam"])
                        bul_map.map[col][row] = {"owner" : "", "shot" : -1, "dam" : 1}
                    elif col > field_height - len(player_graphic) - 1:
                        player.get_dam(dam=bul_map.map[col][row]["dam"])
                        bul_map.map[col][row] = {"owner" : "", "shot" : -1, "dam" : 1}
                else:
                    self.field[col + 1]
                curr_col = self.field[col + 1]
    def print_field(self):
        for _ in self.field:
            stdout.write("\033[F")
        print(*(self.field), sep="\n")
        stdout.flush()


def main():
    player = Entity(hp=10, width=len(player_graphic), pos=rd(1,23), vel=8, bul_dam=1, bul_vel=-8, burst=True, rapid_fire=3, reload=3)
    enemy = Entity(hp=100, width=len(enemy_graphic), pos=rd(2,22), vel=4, bul_dam=1, bul_vel=16, burst=False, rapid_fire=20, reload=3)
    field = Field(player=player, enemy=enemy)
    print(*player_graphic, sep="\n")
    print(*enemy_graphic, sep= "\n")
    print(bul_graphic)
    print(player.pos, enemy.pos)
    print("\n" * 9)
    field.print_field(field)
    print("enemy hp:",enemy.hp,"player hp:",player.hp)
    stdout.flush()
    frame = 0
    for i in range (16):
        sleep(refresh_rate)
        player.change_pos(rd(1,23), frame)
        enemy.change_pos(rd(2,22), frame)
        field = Field(player=player, enemy=enemy)
        stdout.write("\033[F")
        field.print_field(field)
        print("enemy hp:",f"{enemy.hp:3}","player hp:",f"{player.hp:2}")
        stdout.flush()
        frame += 1
    player.change_pos(rd(1,23), frame)
    enemy.change_pos(rd(2,22), frame)
    bul_map = BulMap()
    bul_map.advance_frame(enemy=enemy, player=player, frame=frame)
    bul_map.add_new_bul(entity=enemy, frame=frame)
    bul_map.add_new_bul(entity=player, frame=frame)
    sleep(refresh_rate)
    field = Field(player=player, enemy=enemy, bul_map=bul_map)
    stdout.write("\033[F")
    field.print_field(field)
    print("enemy hp:",f"{enemy.hp:3}","player hp:",f"{player.hp:2}")
    stdout.flush()
    frame += 1
    sleep(refresh_rate)
    for i in range (100):
        sleep(refresh_rate)
        bul_map.advance_frame(enemy=enemy, player=player, frame=frame)
        player.change_pos(rd(1,23), frame)
        enemy.change_pos(rd(2,22), frame)
        field = Field(player=player, enemy=enemy, bul_map=bul_map)
        stdout.write("\033[F")
        field.print_field(field)
        print("enemy hp:",f"{enemy.hp:3}","player hp:",f"{player.hp:2}")
        stdout.flush()
        frame += 1

if __name__ == "__main__":
    main()