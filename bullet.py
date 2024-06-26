from global_variables import field_width, field_height, fps, enemy_graphic, player_graphic


class BulMap:
    def __init__(self):
        self.map = [[{"owner" : "", "shot" : -1, "dam" : 1, "vel" : 16} for row in range(field_width)] for col in range(field_height)]
    #before execute add_new_bul method, execute advance_fram method
    def add_new_bul(self, entity, frame):
        if entity.bul_vel > 0:
            col = len(enemy_graphic)
            owner = "b"
        elif entity.bul_vel < 0:
            col = field_height - len(player_graphic) - 1
            owner = "p"
        self.map[col][entity.pos]["owner"] = owner
        self.map[col][entity.pos]["shot"] = frame
        self.map[col][entity.pos]["dam"] = entity.bul_dam
        self.map[col][entity.pos]["vel"] = entity.bul_vel
    def advance_frame(self, enemy, player, frame):
        new_map = BulMap().map
        for col in range(len(self.map)):
            for row, info in enumerate(self.map[col]):
                if (info["owner"] == "b") and (col < (field_height - 1)):
                    if (frame - self.map[col][row]["shot"]) % (fps // enemy.bul_vel) == 0:
                        if (self.map[col + 1][row]["owner"] != "p") and (new_map[col + 1][row]["owner"] != "p"):
                            new_map[col + 1][row] = info
                        else:
                            new_map[col + 1][row] = {"owner" : "", "shot" : -1, "dam" : 1, "vel" : 16}
                    else:
                        new_map[col][row] = info
                elif (info["owner"] == "p") and (col > 0):
                    if (frame - self.map[col][row]["shot"]) % (fps // player.bul_vel) == 0:
                        if (self.map[col - 1][row]["owner"] != "b") and (new_map[col - 1][row]["owner"] != "b"):
                            new_map[col - 1][row] = info
                        else:
                            new_map[col - 1][row] = {"owner" : "", "shot" : -1, "dam" : 1, "vel" : 16}
                    else:
                        new_map[col][row] = info
        self.map = new_map