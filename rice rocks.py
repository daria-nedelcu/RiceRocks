# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
m_pos = [0, 0]
m_vel = [0, 0]
WRAP = 10
SPAWN_EDGE = 20
SPAWN_VEL = 10
ANGULAR_V = 0.1
DECELERATION = 0.99
ACCELERATION = 0.1
started = False
explosion_group = set([])


class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2013.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_blue2.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def process_sprite_group(aSet, canvas):
    for sprite in list(aSet):
        sprite.draw(canvas)
        sprite.update()
        if sprite.update():
            aSet.remove(sprite)
        
def group_collide(group, other_object):
    result = False
    for sprite in list(group):
        if sprite.collide(other_object):
            group.discard(sprite)
            result = True
            explosion = Sprite(sprite.get_position(), [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
            explosion_group.add(explosion)
    return result       

def group_group_collide(r_group, m_group):
    result = 0
    for rock in list(r_group):
        if group_collide(m_group, rock):
            result += 1
            r_group.discard(rock)
            
    return result
 
    
# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
        
    def draw(self,canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
                          
    def update(self):
        #update angle
        self.angle += self.angle_vel
        
        #update position
        self.pos[0] +=  self.vel[0]
        self.pos[1] +=  self.vel[1]
        
        #acceleration and friction
        if self.thrust == True:
            atv = angle_to_vector(self.angle)
           
            self.vel[0] += ACCELERATION * atv[0]
            self.vel[1] += ACCELERATION * atv[1]
        else:
            self.vel[0] *= DECELERATION
            self.vel[1] *= DECELERATION
        
        #wraping
        if self.pos[0] > WIDTH - WRAP: 
            self.pos[0] = WRAP
        elif self.pos[0] < WRAP: 
            self.pos[0] = WIDTH - WRAP
        elif self.pos[1] > HEIGHT - WRAP : 
            self.pos[1] = WRAP
        elif self.pos[1] < WRAP: 
            self.pos[1] = HEIGHT - WRAP

    def thrusters(self, value):
        if value == True:
            self.image_center[0] += 90
            ship_thrust_sound.play()
            self.thrust = True
        else:
            self.image_center[0] = 45
            ship_thrust_sound.rewind()
            self.thrust = False
     
    def keydown(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.angle_vel += ANGULAR_V
        elif key == simplegui.KEY_MAP['left']:
            self.angle_vel -= ANGULAR_V
        elif key == simplegui.KEY_MAP['up']:
            self.thrusters(True)
        elif key == simplegui.KEY_MAP['space']:
            self.shoot()

    def keyup(self, key):
        if key == simplegui.KEY_MAP['right']:
            self.angle_vel -= ANGULAR_V
        elif key == simplegui.KEY_MAP['left']:
            self.angle_vel += ANGULAR_V
        elif key == simplegui.KEY_MAP['up']:
            self.thrusters(False)
                    
    def shoot(self):
        
        #spawn a new missile
        atv = angle_to_vector(self.angle)
        
        m_pos[0] = self.pos[0] + self.radius * atv[0]
        m_pos[1] = self.pos[1] + self.radius * atv[1]     
        m_vel[0] = self.vel[0] + (atv[0] * 5)
        m_vel[1] = self.vel[1] + (atv[1] * 5)

        a_missile = Sprite(m_pos, m_vel, 0, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
                         
        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        if self.animated == True:
            current_index = self.age % 24
            current_center = [self.image_center[0] +  current_index * self.image_size[0], self.image_center[1]]
            canvas.draw_image(self.image, current_center, self.image_size, self.pos, self.image_size, self.angle) 
            
                       
    def update(self):
        #update angle
        self.angle += self.angle_vel
        
        #update position
        self.pos[0] +=  self.vel[0]
        self.pos[1] +=  self.vel[1]
        
        #wraping
        if self.pos[0] > WIDTH - WRAP: 
            self.pos[0] = WRAP
        elif self.pos[0] < WRAP: 
            self.pos[0] = WIDTH - WRAP
        elif self.pos[1] > HEIGHT - WRAP : 
            self.pos[1] = WRAP
        elif self.pos[1] < WRAP: 
            self.pos[1] = HEIGHT - WRAP
            
        #update age
        self.age +=1
        if self.age >= self.lifespan:
            return True
        else:
            return False

    def collide(self, other_object):    
        d = dist(self.get_position(), other_object.get_position())
        r = self.get_radius() + other_object.get_radius()
        
        if d < r:
            return True
        else:
            return False       
 
def draw(canvas):
    global time
    global lives
    global score
    global rock_group
    global started
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw and update ship 
    my_ship.draw(canvas)
    my_ship.update()
        
    #draw groups
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
    
    
    #draw stats
    canvas.draw_text("LIVES : " + str(lives), [10, 30], 24, "White")
    canvas.draw_text("SCORE : " + str(score), [670, 30], 24, "White")
    
    #collision with the ship
    if group_collide(rock_group, my_ship):
        lives -= 1
    if lives == 0:
        started = False
        rock_group = set([])
        timer.stop()
                
        
    #collisions between rocks and missiles
    score += group_group_collide(rock_group, missile_group)
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started
    global score
    global lives
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        timer.start()
        lives = 3
        score = 0

        
# timer handler that spawns a rock    
def rock_spawner():
        
    pos = [random.randrange(SPAWN_EDGE, WIDTH - SPAWN_EDGE), 
           random.randrange(SPAWN_EDGE, HEIGHT - SPAWN_EDGE)]
    vel = [(random.randrange(-SPAWN_VEL, SPAWN_VEL)) / 10, 
           (random.randrange(-SPAWN_VEL, SPAWN_VEL)) / 10 ]
    angle = (random.randrange(0, 180) / 180) * math.pi
    angle_vel = random.random() * random.choice([-0.05, 0.05])
    
    while dist(pos, my_ship.get_position()) < 100:
        pos = [random.randrange(SPAWN_EDGE, WIDTH - SPAWN_EDGE), 
           random.randrange(SPAWN_EDGE, HEIGHT - SPAWN_EDGE)]
        
    a_rock = Sprite(pos, vel, angle, angle_vel, asteroid_image, asteroid_info)
    if len(rock_group) <= 12:
        rock_group.add(a_rock)

#key handlers

def kdown(key):
    my_ship.keydown(key)
  
def kup(key):
    my_ship.keyup(key)
      
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
#a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, 0, asteroid_image, asteroid_info)
rock_group = set([])
#a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, missile_sound)
missile_group = set([])

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(kdown)
frame.set_keyup_handler(kup)
frame.set_mouseclick_handler(click)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
#timer.start()
frame.start()
