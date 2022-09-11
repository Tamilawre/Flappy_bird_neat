import pygame
import os
import random
from sys import exit
import time
import neat

pygame.init()
pygame.mixer.pre_init(44100, 16, 2, 4096)
width, height = 300, 500

# sounds
point_sound = pygame.mixer.Sound("Sounds/point.ogg")
flap_sound = pygame.mixer.Sound("Sounds/wing.ogg")
die_sound = pygame.mixer.Sound("Sounds/die.ogg")
hit_sound = pygame.mixer.Sound("Sounds/hit.ogg")

player_colour = (235, 220, 0)
pipe_green = (10, 134, 18)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy bird")
# stores a list of all our score text images
score_image_list = []
text_container = pygame.Surface((50, 60))
text_container.fill("white")

text_surface = pygame.font.Font(None, 30)
gen_surface = pygame.font.Font(None, 30)
platform = pygame.image.load("Images/flappy_bird_background.png").convert()
platform_rect = platform.get_rect(topleft=(0, height - height / 5))
angle = 0
background = pygame.image.load("Images/f_background.png").convert()


class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        # self.fitness = 0
        # our bird images
        self.image_list = ["Images/flap1.png", "Images/flap2.png", "Images/flap3.png"]
        self.state = 0
        self.index = self.image_list[self.state]
        self.player = pygame.image.load(self.index).convert_alpha()
        self.player_rect = self.player.get_rect(topleft=(self.x, self.y))

        self.acceleration_value = 0
        self.flight_time = 0

    def draw(self):
        global platform_rect
        self.player_copy = pygame.transform.rotate(self.player, self.angle)
        screen.blit(self.player_copy, self.player_rect)
        # screen.blit(self.player_copy, (self.x - int(self.player_copy.get_width()/2), self.y - int(self.player_copy.get_height()/2)))
        self.acceleration_value += 0.01
        if self.angle != -90:
            self.angle -= 5

    def flap(self):
        #for i in range(len(self.image_list)):
        # print(self.state)
        if self.state == 3:
            self.state = 0

        self.player = pygame.image.load(self.image_list[self.state]).convert_alpha()
        self.state += 1
        self.acceleration_value = 0
        self.flight_time += 0.05
        # if self.flight_time > 0:
        self.player_rect.y -= 3 + self.flight_time
        if self.angle != 30:
            self.angle = 20
    # the acceleration value simulates gravity by making the players movement not constant


class Pipes:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.top_pipe = pygame.image.load("Images/long_pipe0.png")
        self.top_pipe_rect = self.top_pipe.get_rect(topleft=(x, y))
        self.space_between = 100
        self.bottom_pipe = pygame.image.load("Images/long_pipe.png")
        self.bottom_pipe_rect = self.bottom_pipe.get_rect(topleft=(x, y + self.space_between + 200))

    def draw(self):
        screen.blit(self.top_pipe, self.top_pipe_rect)
        screen.blit(self.bottom_pipe, self.bottom_pipe_rect)


pipe_list = []
score_list = []


def generate_pipes():
    global pipe_list
    global pipe_green
    pipe_list = []
    x = width
    pipe_space = 160
    for i in range(5):
        pipe = Pipes(x, random.randrange(-110, 0))
        x += pipe_space
        pipe_list.append(pipe)



gen = 0
def main(genomes, config):
    nets = []
    ge = []
    birds = []
    global gen
    global image_list
    global pipe_list
    for _, g in genomes:
        bird = Bird(100, 150)
        birds.append(bird)
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        ge.append(g)

    clock = pygame.time.Clock()
    count_time = 0
    start_count = True
    active = True
    timer = 0

    # generate_time = 160
    is_running = True
    score = 0
    disabled = False
    pipe_speed = 2
    bird_list = []
    bird_x = 100
    bird_y = 150
    run  = True
    pipe_ind = 0
    generate_pipes()

    while run:
            mouse = pygame.mouse.get_pressed()[0]
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or not is_running:
                    time.sleep(1)
                    pygame.quit()
                    exit()
            if len(birds) == 0:
                run = False
                gen += 1

            # for x, bird in enumerate(birds):



            screen.blit(background, (0, -100))
            # if len(birds) > 0:
            #     if len(pipe_list) > 1 and birds[0].x > pipe_list[0].x+ 60:
            #         pipe_ind += 1

            # we have to enurmerate over pipes and birds next
            for pipe in pipe_list:
                pipe.draw()
                pipe.top_pipe_rect.x -= pipe_speed
                pipe.bottom_pipe_rect.x -= pipe_speed
                # print(pipe.top_pipe_rect.x)
                if pipe.top_pipe_rect.x + 60 == bird_x and len(birds) > 0:
                    score += 1
                    pipe_ind += 1
                    if pipe_ind == 5:
                        pipe_ind = 0
                    # print(pipe_ind)
                    point_sound.play()
                    for g in ge:
                        g.fitness += 5
                if pipe.top_pipe_rect.x < -60:
                    # pipe_list.remove(pipe)
                    pipe.y = random.randrange(-90, 0)
                    pipe.top_pipe_rect.x = 740
                    pipe.bottom_pipe_rect.x = 740

            for x, bird in enumerate(birds):
                bird.draw()
                ge[x].fitness += 0.1
                output = nets[x].activate((bird.player_rect.y, pipe_list[pipe_ind].top_pipe_rect.y+200, pipe_list[pipe_ind].bottom_pipe_rect.y))
                # print(pipe_list[pipe_ind].top_pipe_rect.y + 200)
                if output[0] > 0.5:
                    bird.flap()
                else:
                    pass
                for pipe in pipe_list:
                    if bird.player_rect.colliderect(pipe.top_pipe_rect) or bird.player_rect.colliderect(
                        pipe.bottom_pipe_rect):
                        hit_sound.play()
                        ge[x].fitness -= 1
                        birds.pop(x)
                        nets.pop(x)
                        ge.pop(x)
                    # if mouse:
                    #     bird.flap()
                if not bird.player_rect.colliderect(platform_rect):
                    bird.player_rect.y += 3 + bird.acceleration_value
                if bird.player_rect.colliderect(platform_rect) or bird.player_rect.y < 0:
                    hit_sound.play()
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
            gen_number = gen_surface.render("Gen: " + str(gen), False, "white")
            score_text = text_surface.render("Score: " + str(score), False, "white")
            screen.blit(gen_number, (width / 8 - len(str(gen)) * 30 / 2, 10))
            screen.blit(score_text, (width / 8 - len(str(score)) * 30 / 2, 30))
            screen.blit(platform, platform_rect)
            pygame.display.update()


def run(config_path):
    config = neat.Config(neat.DefaultGenome,
                         neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)
    # show the networks progress in the terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations
    winner = p.run(main, 50)

    # Display the winner genome in the terminal
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'NEAT_config')
    run(config_path)





    # next i will use pygame.get_ticks or any other time function to fix the flapping
    # this duration in change between the time the button was held down with the time the button was released
    # will determine when our network will make a decision
