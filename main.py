import pygame
import sys
import math
import random

#window
pygame.init()
WIDTH, HEIGHT = 800,600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planets and lightray simulation")

#constants
FPS = 144
dt = 1/FPS
G = 1
clock = pygame.time.Clock()


#color
WHITE = (255,255,255)
BLACK = (0,0,0)

class Planet:
    def __init__(self, pos, mass, color):
        self.pos = pos
        self.mass = mass
        self.color = color
        self.v = (0,0,0)
        self.a = (0,0,0)
    
    def update(self, ents):
        self.apply_gravity(ents)
        for i in range(3):  # x, y, z
            self.v[i] += self.a[i]
            self.pos[i] += self.v[i]
            self.a[i] = 0

        pygame.draw.circle(window, WHITE, (self.pos[0], self.pos[1]), (self.mass-self.pos[2])//10)
    def apply_gravity(self,ents):

        for ent in ents:
            if ent != self:
                
                # displacement vector
                dx = ent.pos[0] - self.pos[0]
                dy = ent.pos[1] - self.pos[1]
                dz = ent.pos[2] - self.pos[2]

                # distance
                r = math.sqrt(dx**2 + dy**2 + dz**2)

                # masses
                m1, m2 = self.mass, ent.mass

                # force magnitude
                F = G * (m1 * m2) / r**2

                # normalize direction
                dx /= r
                dy /= r
                dz /= r

                # force vector
                Fx = F * dx
                Fy = F * dy
                Fz = F * dz

                self.acc[0] += Fx
                self.acc[1] += Fy
                self.acc[2] += Fz

planets = [Planet((random.randint(0, window.get_width()), random.randint(0, window.get_height()), random.randint(0,100)), 1000, (255,255,255))]    
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #fill
    window.fill(BLACK)

    #draw
    for p in planets:
        p.update(planets)
    
    #update
    pygame.display.update()

pygame.quit()
sys.exit()