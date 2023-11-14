'''Inlcude plasmid loss, include conjugation rate for each pairwise (n= 3! = 6)
    Include visualization of fate of the plasmid under different circumstances
    Aim is to visualize the dilution effect
    Could include change in fitness by plasmid acquisition (dies more quickly, duplicates more slowly)
    Could even include area in the plot with TPA where having plasmid is beneficial'''


import pandas as pd
import pygame
import random
import math
import numpy as np
import datetime
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()
init_time = datetime.datetime.now()


# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)
BACTERIA_COLORS = ['red', 'blue', 'green']
BACTERIA_PERCENTAGES = [0.1, 0.3, 0.6]
BACTERIA_RADIUS = 10
PLASMID_RADIUS = 5
NUM_BACTERIA = 50

# User-defined parameters for bacteria death rates
lifespan_mean_dic = {'red': 8, 'blue': 8, 'green': 8}  # Mean death rate for each color
lifespan_stddev_dic = {'red': 1, 'blue': 1, 'green': 1}  # Standard deviation for each color
duplication_dic = {'red': 4, 'blue': 4, 'green': 4}  # Mean lifespan for each color


# Define text box
font = pygame.font.Font(None, 36)
def draw_text_box(text):
    font = pygame.font.Font(None, 36)

    pygame.draw.rect(screen, 'blue', (10, 10, WIDTH - 20, 50))
    pygame.draw.rect(screen, 'black', (10, 10, WIDTH - 20, 50), 2)

    text_surface = font.render(text, True, 'black')
    screen.blit(text_surface, (20, 20))

# Define Bacteria class
class Bacteria:
    def __init__(self, ID, x, y, color, speed, has_plasmid, lifespan_mean, lifespan_stddev, duplication_rate, time_of_last_duplication):
        self.ID = ID
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.has_plasmid = has_plasmid
        self.lifespan_mean = lifespan_mean
        self.lifespan_stddev = lifespan_stddev
        self.lifespan = np.random.normal(lifespan_mean, lifespan_stddev)
        self.duplication_rate = duplication_rate
        self.time_of_last_duplication = time_of_last_duplication

    def move(self):
        angle = random.normalvariate(0, 1 * math.pi)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

    def duplicate(self, new_ID):
        x_offset = random.uniform(-10, 10)
        y_offset = random.uniform(-10, 10)
        new_bacteria = Bacteria(new_ID, self.x + x_offset, self.y + y_offset, self.color, self.speed, self.has_plasmid,
                                self.lifespan_mean, self.lifespan_stddev, self.duplication_rate, self.time_of_last_duplication)

        return new_bacteria



# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bacteria Simulation")

# Create bacteria objects
bacteria_dic = {}
for i in range(NUM_BACTERIA):
    if i <= BACTERIA_PERCENTAGES[0] * NUM_BACTERIA:
        color = BACTERIA_COLORS[0]
    elif BACTERIA_PERCENTAGES[0] * NUM_BACTERIA < i <= BACTERIA_PERCENTAGES[1] * NUM_BACTERIA:
        color = BACTERIA_COLORS[1]
    else:
        color = BACTERIA_COLORS[2]
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.uniform(2, 6)
    has_plasmid = (color == 'red')  # Red bacteria have plasmids
    ID = i
    bacteria = Bacteria(ID, x, y, color, speed, has_plasmid,
                        lifespan_mean_dic[color], lifespan_stddev_dic[color], duplication_dic[color], time_of_last_duplication=init_time)
    bacteria_dic[i] = bacteria

count = 0
death_count = 0
count_duplication = 0
red_points, blue_points, green_points = [], [], []
plotting_dic = {}
birth_dic = {}
# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Calculate elapsed time
    current_time = datetime.datetime.now()
    time_elapsed = (current_time-init_time).total_seconds()

    # Clear the screen
    screen.fill(BACKGROUND_COLOR)

    # cells to kill and duplicate
    to_be_killed = []
    to_be_born = []
   # print(f'count {count}')
    count += 1

    # Update and draw bacteria
    for id, bacteria in bacteria_dic.items():
        bacteria.move()
        pygame.draw.circle(screen, bacteria.color, (int(bacteria.x), int(bacteria.y),), BACTERIA_RADIUS)
        if bacteria.has_plasmid:
            pygame.draw.circle(screen, (0, 0, 0), (int(bacteria.x), int(bacteria.y),), PLASMID_RADIUS)

        # Check for plasmid transfer
        for other_bacteria in bacteria_dic.values():
            if other_bacteria != bacteria and bacteria.has_plasmid and not other_bacteria.has_plasmid:
                distance = math.sqrt((bacteria.x - other_bacteria.x) ** 2 + (bacteria.y - other_bacteria.y) ** 2) / 2
                if distance < BACTERIA_RADIUS:
                    other_bacteria.has_plasmid = True

        # Check if the bacteria has exceeded its lifespan and remove it
        if time_elapsed - bacteria.lifespan >= bacteria.lifespan:
            to_be_killed.append(id)
        else: pass

        # Check if the bacteria should duplicate
        if (current_time - bacteria.time_of_last_duplication).total_seconds() >= bacteria.duplication_rate:
            bacteria.time_of_last_duplication = datetime.datetime.now()
            count_duplication += 1
            new_id = len(bacteria_dic.keys()) + count_duplication
            new_bacteria = bacteria.duplicate(new_id)
            to_be_born.append([new_id, new_bacteria, bacteria])

    # kill and born
    for id in to_be_killed:
        bacteria = bacteria_dic[id]
        bacteria_dic.pop(id)
        death_count += 1


    for elem in to_be_born:
        new_id = elem[0]
        new_bacteria = elem[1]
        mother_bacteria = elem[2]
        bacteria_dic[new_id] = new_bacteria
        birth_dic[mother_bacteria.ID] = new_bacteria.ID

    total_bacteria_now = len(bacteria_dic.keys())
    red_bacteria = len([bacteria.color for bacteria in bacteria_dic.values() if bacteria.color == 'red'])
    blue_bacteria = len([bacteria.color for bacteria in bacteria_dic.values() if bacteria.color == 'blue'])
    green_bacteria = len([bacteria.color for bacteria in bacteria_dic.values() if bacteria.color == 'green'])

    if total_bacteria_now > 0:
        draw_text_box(f'Percetange of red: {round((red_bacteria/total_bacteria_now), 2)}, blue: {round((blue_bacteria/total_bacteria_now), 2)} and green {round((green_bacteria/total_bacteria_now), 2)}')
    red_points.append((red_bacteria, time_elapsed))
    blue_points.append((blue_bacteria, time_elapsed))
    green_points.append((green_bacteria, time_elapsed))
    plotting_dic['red'] = red_points
    plotting_dic['blue'] = blue_points
    plotting_dic['green'] = green_points


    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.delay(30)
    print(f'Birth dic: {birth_dic}')
    #print(bacteria_dic)

# Quit Pygame
pygame.quit()


fig, ax = plt.subplots()
for color, plot_list in plotting_dic.items():
    y_values, x_values = zip(*plot_list)
    x_values = [x_values[0]] + list(x_values)  # Duplicate the first x-value to match edges
    ax.stairs(y_values, x_values, fill=False, color=color, alpha=0.5, label=color)

plt.xlim(2, 40)
plt.show()
plt.close()

now = datetime.datetime.now()
print(f'Game took {(now-init_time).total_seconds()}')
print(f'Death count {death_count}')
print(f'Duplication count {count_duplication}')
