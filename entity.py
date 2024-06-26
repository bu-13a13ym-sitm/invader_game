from global_variables import field_width, fps, player_graphic
from bullet import BulMap
from random import randint as rd

class Entity:
    def __init__(self,*, hp=0, width=0, pos=rd(2, 22), vel = 0, bul_dam=0, bul_vel=1, burst=False, rapid_fire=0, reload=0):
        self.max_hp = hp
        self.hp = hp
        self.width = width
        self.pos = pos
        self.vel = vel
        self.bul_dam = bul_dam
        self.bul_vel = bul_vel
        self.burst = burst
        self.fire_rate = (int(not self.burst) + 1) * (fps / bul_vel)
        self.rapid_fire = rapid_fire
        self.firing = False
        self.rapid_fire_start = -1
        self.fire_count = 0
        self.reload = reload * fps
        self.reloading = False
        self.reload_start = -1
    def get_dam(self, own="", dam = 1):
        self.hp -= dam
    def change_bul_dam(self, new_dam):
        self.bul_dam = new_dam
    def change_pos(self, new_pos, frame):
        pos = self.pos
        half_width = self.width//2
        if (pos != new_pos) and ((new_pos >= half_width) and (new_pos < field_width - half_width)) and ((frame % (fps // self.vel)) == 0):
            if new_pos > self.pos:
                self.pos += 1
            elif new_pos < self.pos:
                self.pos -= 1
    def begin_rapid_fire(self, frame=-1, bul_map=BulMap()):
        bul_map.add_new_bul(self, frame)
        self.firing = True
        self.fire_count += 1
        self.rapid_fire_start = frame
    def rapid_fire_manager(self, frame, bul_map=BulMap()):
        if abs(frame - self.rapid_fire_start) % self.fire_rate == 0:
            bul_map.add_new_bul(self, frame)
            self.fire_count += 1
    def end_rapid_fire(self, frame=-1):
        self.firing = False
        self.rapid_fire_start = -1
        self.fire_count = 0
        self.reloading = True
        self.reload_start = frame
    def reload_manager(self, frame=-1):
        if abs(frame - self.reload_start) == self.reload:
            self.reloading = False
            self.reload_start = -1
    def fire(self, frame, bul_map=BulMap(), input=rd(0,1)):
        if self.reloading:
            self.reload_manager(frame)
        elif self.firing:
            if self.fire_count < self.rapid_fire:
                self.rapid_fire_manager(frame, bul_map)
            else:
                self.end_rapid_fire(frame)
        elif not input:
            self.begin_rapid_fire(frame, bul_map=bul_map)


"""
boss:
boss.fire(frame)

player:
player.fire(frame, switch_input)
"""