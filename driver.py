import math
import random
import pygame
import sprites
import nndraw
import utils


class Simulation:
    def __init__(self):
        # display and window info
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.clock = pygame.time.Clock()
        # pygame.display.set_caption('MLGame')
        self.white = (255, 255, 255)
        self.screen.fill(self.white)

        self.clock_speed = 300

        # instantiate object player of class Player
        self.blue = (0, 0, 128)
        self.player = sprites.Player((self.screen_width * random.random(), self.screen_height * random.random()), self.blue, self.screen_width, self.screen_height)

        # spear = sprites.Spear((screen_width * .75, screen_height * .5), screen_width, screen_height)

        # instantiate object player of class AI
        self.n_ais = 7
        self.ais = [sprites.AI((self.screen_width * random.random(), self.screen_height * random.random()), self.screen_width, self.screen_height) for count in range(self.n_ais)]
        # print(len(self.ais))
        self.n_food = 5
        self.food_list = [sprites.Food((self.screen_width * random.random(), self.screen_height * random.random())) for count in range(self.n_food)]
        self.entities = [self.player] + self.ais + self.food_list
        self.selected_obj = None
    
    def select_obj(self, touch_coords):
        self.selected_obj = None
        closest_obj_dist = math.inf
        for obj in self.entities:
            obj_dist = utils.distance_formula(touch_coords[0], touch_coords[1], obj.x, obj.y)
            if obj_dist < closest_obj_dist:
                self.selected_obj = obj
                closest_obj_dist = obj_dist
        return self.selected_obj

sim = Simulation()
nnd = nndraw.MyScene(sim.screen, (sim.screen_width, sim.screen_height))

while True:
    sim.screen.fill(sim.white)

    # if spear.destroyed:
    #     spear = sprites.Spear((screen_width * .75, screen_height * .5), screen_width, screen_height)

    for ai in sim.ais:
        if ai.user_select:
            nnd.draw(ai.nn)

    # draw player
    # pygame.draw.rect(screen, player.color, player.rect, 2)
    # pygame.draw.rect(screen, spear.color, spear.rect, 2)
    [pygame.draw.rect(sim.screen, ai.color, ai.rect, 2) for ai in sim.ais]
    [pygame.draw.rect(sim.screen, food.color, food.rect, 2) for food in sim.food_list]

    # check for users key pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
            if event.key == pygame.K_f:
                clock_speed += 10
            if event.key == pygame.K_s:
                clock_speed -= 10
        if event.type == pygame.MOUSEBUTTONUP:
            if sim.selected_obj is not None:
                sim.selected_obj.user_select = False
            selected_obj = sim.select_obj(pygame.mouse.get_pos())
            selected_obj.user_select = True

    # checking pressed held
    # keys = pygame.key.get_pressed()
    # if keys[pygame.K_s]:
    #     with open("nn.txt", "w") as file_out:
    #         file_out.write(str(ai.nn))
    # if keys[pygame.K_s]:
    #     clock_speed -= 10
    # if keys[pygame.K_f]:
    #     clock_speed += 10
    # if keys[pygame.K_a]:
    #     player.move(-player.speed, 0)

    # spear.update()
    # update player
    # player.auto(ai)
    # update ai
    # print(ai.alive)

    # if ai dies reset the game
    # if not ai.alive:
    #     ai.reset()
        # player.reset()

    [ai.update(sim.entities) for ai in sim.ais]
    [food.destroy() for food in sim.food_list if random.random() <= 0.0001]
    sim.ai = [ai for ai in sim.ais if ai.alive]
    sim.food_list = [food for food in sim.food_list if food.alive]
    sim.food_list = sim.food_list + [sprites.Food((sim.screen_width * random.random(), sim.screen_height * random.random()))] if len(sim.food_list) <= sim.n_food else sim.food_list
    sim.entities = [sim.player] + sim.ais + sim.food_list

    sim.clock.tick(sim.clock_speed)

    # update display
    pygame.display.update()
