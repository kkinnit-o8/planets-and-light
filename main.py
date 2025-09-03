import pygame
import sys
import math
import random
import numpy as np

# window
pygame.init()
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planets and lightray simulation")

# constants
FPS = 144
dt = 1 / FPS
G = 1
clock = pygame.time.Clock()
C = 1000 #light speed
LIGHT_MASS = 10000

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Camera:
    def __init__(self, x=0, y=0, z=-500):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 1000
        self.focal_length = 500  # how strong perspective is

    def move(self, keys):
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_q]:
            self.z += self.speed  # move camera forward
        if keys[pygame.K_e]:
            self.z -= self.speed  # move camera backward


def gravity_force(ent2,ent1):
            
            dx = ent1.pos[0] - ent2.pos[0]
            dy = ent1.pos[1] - ent2.pos[1]
            dz = ent1.pos[2] - ent2.pos[2]

            # distance
            r = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
            if r == 0:
                return None

            m1, m2 = ent2.mass, ent1.mass

            # force magnitude
            F = G * (m1 * m2) / r ** 2

            # normalize direction
            dx /= r
            dy /= r
            dz /= r

            # acceleration = F / m1
            ent2.a[0] += (F * dx) / m1
            ent2.a[1] += (F * dy) / m1
            ent2.a[2] += (F * dz) / m1


class Planet:
    def __init__(self, pos, mass, color, density):
        self.pos = list(pos)  # [x, y, z]
        self.mass = mass
        self.color = color
        self.v = [0, 0, 0]  # velocity
        self.a = [0, 0, 0]  # acceleration
        self.density = density

    def update(self, ents):
        self.apply_gravity(ents)

        # update velocity and position
        for i in range(3):  # x, y, z
            self.v[i] += self.a[i]
            self.pos[i] += self.v[i]
            self.a[i] = 0  # reset acceleration

    def apply_gravity(self, ents):
        for ent in ents:
            if ent != self:
                gravity_force(self,ent)
    
    def emit_rays_from_pixels(self, camera, rays_list):

        # Calculate displacement relative to camera
        dx = self.pos[0] - camera.x
        dy = self.pos[1] - camera.y
        dz = self.pos[2] - camera.z

        if dz <= 0:
            return  # planet is behind the camera

        # Project planet to screen coordinates
        screen_x = int(WIDTH / 2 + (dx / dz) * camera.focal_length)
        screen_y = int(HEIGHT / 2 + (dy / dz) * camera.focal_length)

        # Calculate radius of the planet on screen
        radius = max(1, int((self.mass / self.density) * camera.focal_length / dz))

        # Loop over pixels inside the projected circle
        for px in range(-radius, radius + 1):
            for py in range(-radius, radius + 1):
                if px**2 + py**2 <= radius**2:
                    pixel_x = screen_x + px
                    pixel_y = screen_y + py

                    # Only emit rays that are visible on the screen
                    if 0 <= pixel_x < WIDTH and 0 <= pixel_y < HEIGHT:
                        # Convert screen pixel back to approximate world coordinates
                        world_x = camera.x + (pixel_x - WIDTH / 2) * dz / camera.focal_length
                        world_y = camera.y + (pixel_y - HEIGHT / 2) * dz / camera.focal_length
                        world_z = self.pos[2]  # start at planet's depth

                        # Emit light ray toward camera (-z direction)
                        rays_list.append(light_ray(pos=[world_x, world_y, world_z]))


        
        


class light_ray:
    def __init__(self, pos, m=LIGHT_MASS, v=[0,0,-C]):
        self.mass = m
        self.pos = pos
        self.v = v
        self.a = [0,0,0]



# create planets
planets = [
Planet( (random.randint(-10*10**3, 10*10**3), random.randint(-10*10**3, 10*10**3), random.randint(100, 2000)), random.randint(500, 1500), (random.randint(0,255),random.randint(0,255),random.randint(0,255)), random.randint(20,100) ) for _ in range(100)
]
planets.append(Planet([0,0,0], 10e5, WHITE, 10e4))

# create camera
camera = Camera(z=-21500)

rays = []
# Initialize a black screen array
pixels = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    print(camera.z)
    keys = pygame.key.get_pressed()
    camera.move(keys)

    #fill
    pixels.fill(2)
    
    for planet in planets:
        planet.update(planets)
        planet.emit_rays_from_pixels(camera, rays)
    
    for ray in rays[:]:  # iterate over a copy
        ray.a = [0, 0, 0]

        for planet in planets:
            gravity_force(ray, planet)

        # update velocity and position
        for i in range(3):
            ray.v[i] += ray.a[i] * dt
            ray.pos[i] += ray.v[i] * dt

        # only draw if the ray has passed the camera
        if ray.pos[2] >= camera.z:  # ray is beyond camera
            dz = ray.pos[2] - camera.z
            dx = ray.pos[0] - camera.x
            dy = ray.pos[1] - camera.y

            screen_x = int(WIDTH / 2 + dx / dz * camera.focal_length)
            screen_y = int(HEIGHT / 2 + dy / dz * camera.focal_length)

            if 0 <= screen_x < WIDTH and 0 <= screen_y < HEIGHT:
                pixels[screen_y, screen_x] = [255, 255, 255]

            rays.remove(ray)
            continue

        # remove rays that go too far
        if ray.pos[2] > 5000:
            rays.remove(ray)

    pygame.surfarray.blit_array(window, pixels.transpose(1, 0, 2))
    pygame.display.update()

pygame.quit()
sys.exit()
