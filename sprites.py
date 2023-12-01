import random
from random import sample
import math
import time
import pygame
from numpy import exp
import numpy as np


class Player(object):
    def __init__(self, coord, color, screen_width, screen_height):
        self.x = coord[0]
        self.y = coord[1]
        self.focused = None
        self.start_x = self.x
        self.start_y = self.y
        self.rect = pygame.rect.Rect((self.x, self.y, 50, 50))
        self.rect.center = (self.x, self.y)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = color
        self.start_health = 100
        self.health = self.start_health
        self.speed = 1
        self.attack_damage = 25
        self.last_attack_time = 0
        self.time_betw_attacks = 1
        self.mode = "peaceful"
        self.user_select = False
        self.alive = True

    def move(self, direc):
        self.x = (self.x + direc[0]) % self.screen_width
        self.y = (self.y + direc[1]) % self.screen_height
        self.rect.center = (self.x, self.y)

    def can_attack(self):
        if time.time() - self.last_attack_time >= self.time_betw_attacks:
            self.last_attack_time = time.time()
            return True

    def direction_focused(self):
        v = np.subtract((self.focused[0], self.focused[1]), (self.x, self.y))
        normalized_v = v / np.linalg.norm(v)
        return normalized_v * self.speed

    def focus(self, obj):
        self.focused = (obj.x, obj.y)

    def auto(self, obj):
        self.focus(obj)
        self.move(self.direction_focused())

    def reset(self):
        self.x = self.screen_width * random.random()
        self.y = self.screen_height * random.random()
        self.rect.center = (self.start_x, self.start_y)
        self.health = self.start_health


class AI(object):
    def __init__(self, coord, screen_width, screen_height):
        self.x = coord[0]
        self.y = coord[1]
        self.start_x = self.x
        self.start_y = self.y
        self.rect = pygame.rect.Rect((self.x, self.y, 50, 50))
        self.rect.center = (self.x, self.y)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = (0, 0, 0)
        self.color_need_reset = False
        self.color_time_change = 0
        self.color_chng_wait_time = 1
        self.color_multi = 25
        self.touch_time = time.time() - 1
        self.objs = None
        self.age = 0
        self.iter_age = 0
        self.start_health = 100
        self.health = self.start_health
        self.focused_obj = None
        self.score = 0
        self.speed = 1
        self.coord_changes = [(self.speed, 0), (-self.speed, 0), (0, self.speed), (0, -self.speed)]
        self.layers = [4, 7, len(self.coord_changes)]
        self.nn = list()
        self.nn = [[[random.uniform(-1, 1) for weight in range(self.layers[l_idx + 1])] for node in range(self.layers[l_idx])] for l_idx in range(len(self.layers) - 1)]
        self.output = 0
        self.mutation_multi = 2
        self.alive = True
        self.user_select = False
        self.mode = "peaceful"

    @staticmethod
    def softmax(vector):
        e = exp(vector)
        return e / e.sum()  

    def mutate_nn(self, min_update, max_update):
        # print("Positive Stimulus", self.iter_age) if max_update - 1 >= 1 - min_update else print("Negative Stimulus")
        self.nn = [[[weight * random.uniform(min_update, max_update) for weight in node] for node in layer] for layer in self.nn]

    def propagate(self, inputs):
        # create the amount of outputs for up, down, left, right
        outputs = [[0 for node in range(layer_size)] for layer_size in self.layers]
        for l_idx in range(len(self.nn)):
            for n_idx in range(len(self.nn[l_idx])):
                for w_index in range(len(self.nn[l_idx][n_idx])):
                    if l_idx == 0:
                        outputs[l_idx + 1][w_index] += inputs[n_idx] * self.nn[l_idx][n_idx][w_index]
                    else:
                        outputs[l_idx + 1][w_index] += outputs[l_idx][n_idx] * self.nn[l_idx][n_idx][w_index]
        return self.softmax(outputs[-1])

    def search(self, class_type):
        closest_res_dist = math.inf
        for obj in self.objs:
            obj_dist = self.distance_formula(obj.x, obj.y)
            # check if did not find self, since self will match criteria and is in list of objects to check
            if isinstance(obj, class_type) and obj_dist <= closest_res_dist and id(self) != id(obj):
                closest_res_dist = obj_dist
                self.focused_obj = obj

    def think(self):
        # self.search(Food)
        # inputs = self.get_opp_inputs(opponent) + [self.speed, self.health, self.speed, distance]
        # print(self.distance_formula(self.focused_obj.x, self.focused_obj.y))
        # inputs = [self.iter_age,
        #           self.distance_formula(self.objs[0].x, self.objs[1].y)
        #           ]
        inputs = [self.x,
                  self.y,
                  self.objs[0].x,
                  self.objs[0].y,
                  ]
        # inputs = [self.distance_formula(self.focused_obj.x, self.focused_obj.y), self.focused_obj.x, self.focused_obj.y, self.x, self.y]
        outputs = list(self.propagate(inputs))
        self.output = outputs.index(max(outputs))
        # might need multiple nns for multiple outputs?
        # print(self.output)
        self.move(self.output)
        # attack
        # defense/offense
        # ...

    def update_time(self):
        if time.time() - self.touch_time >= 5:
            self.mutate_nn(0.95, 0.99)
            self.touch_time = time.time()
            # self.score //= 2

    def distance_formula(self, x2, y2):
        return math.sqrt(((x2 - self.x) ** 2) + ((y2 - self.y) ** 2))

    def update(self, objs):
        self.objs = objs
        if self.iter_age % 100 == 1:
            # self.mutate_nn(math.log(0.99 * self.iter_age, 50), math.log(1.1 * self.iter_age, 50))
            self.mutate_nn(0.995, 1.005)
        self.iter_age += 1
        self.think()
        self.detect_collision()
        # self.update_time()
        if self.color_need_reset and time.time() - self.color_time_change >= self.color_chng_wait_time:
            self.change_color()

    def move(self, choice_index):
        coord_change = self.coord_changes[choice_index]
        self.x = (self.x + coord_change[0]) % self.screen_width
        self.y = (self.y + coord_change[1]) % self.screen_height
        self.rect.center = (self.x, self.y)

    def detect_collision(self):
        for obj in self.objs:
            if obj.mode == "peaceful":
                continue
            if time.time() - self.touch_time >= 0.25 and obj.rect.colliderect(self.rect) and isinstance(obj, Food):
                self.score += obj.score_inc
                self.color = (0, 255, 0)
                self.color_need_reset = True
                self.color_time_change = time.time()
                self.mutate_nn(0.9, 1.5)
                self.touch_time = time.time()
                obj.destroy()
            if obj.rect.colliderect(self.rect) and isinstance(obj, Player):
                self.mutate_nn(0.99, 1.01)
                self.die()

    def reset(self):
        # self.mutate()
        self.x = self.screen_width * random.random()
        self.y = self.screen_height * random.random()
        self.rect.center = (self.start_x, self.start_y)
        self.iter_age = 0
        self.health = self.start_health
        self.alive = True
        self.change_color()

    def change_color(self):
        # red = 30 + (1 / (0.0045 + math.exp(-self.speed)))
        red = 1 / (0.0039381 + math.exp(-self.speed * self.color_multi))
        green = self.score if self.score <= 255 else 255
        blue = self.color[2]
        self.color = (red, green, blue)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    def mutate(self):
        bounded_age = (1 - self.sigmoid(self.age)) * self.mutation_multi

        # update how much mutation changes attributes of ai after each death
        # the reason is so that if the ai needs to change its attributes faster it can
        self.mutation_multi *= random.uniform(1 - bounded_age, 1 + bounded_age)

        # mutate speed
        self.speed *= random.uniform(1 - bounded_age, 1 + bounded_age)
        self.change_color()

        # update the speed for coord_changes
        self.coord_changes = [(0, self.speed), (0, -self.speed), (self.speed, 0), (-self.speed, 0)]

        self.mutate_nn()

    def die(self):
        self.alive = False
        # self.age = self.tod - self.tob
        # self.mutate()
        # print(self.age)

    def debug(self):
        print(f"score: {self.score}")
        print(f"nn:    {self.nn}")
        print(f"reset:    {time.time() - self.touch_time >= self.score + 2 ** 1.1} ({time.time() - self.touch_time})")
        # print(f"speed:          {self.speed}")
        # # todo: print weight of nn
        # print(f"output:         {self.output}")
        # print(f"mutation_multi: {self.mutation_multi}")
        # print(f"rect:           {self.rect}")
        # print(f"color:          {self.color}")
        # print()


class Spear(object):
    def __init__(self, coord, screen_width, screen_height):
        self.x = coord[0]
        self.y = coord[1]
        self.start_x = self.x
        self.start_y = self.y
        self.rect = pygame.rect.Rect((self.x, self.y, 50, 10))
        self.rect.center = (self.x, self.y)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = (125, 0, 0)
        self.incr = -0.5
        self.destroyed = False
        self.score_decr = 2
        self.user_select = False
        self.alive = True

    def move(self):
        self.x += self.incr
        self.y += 0
        self.rect.center = (self.x, self.y)
        if self.x <= 0:
            self.destroy()

    def destroy(self):
        self.destroyed = True

    def update(self):
        if not self.destroyed:
            self.move()

    def reset(self):
        self.x = self.screen_width * random.random()
        self.y = self.screen_height * random.random()
        self.rect.center = (self.start_x, self.start_y)


class Food(object):
    def __init__(self, coord):
        self.x = coord[0]
        self.y = coord[1]
        self.rect = pygame.rect.Rect((self.x, self.y, 20, 20))
        self.rect.center = (self.x, self.y)
        self.color = (0, 125, 00)
        self.score_inc = 2
        self.alive = True
        self.mode = "normal"
        self.user_select = False

    def destroy(self):
        self.alive = False
