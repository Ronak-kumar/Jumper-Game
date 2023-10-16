# Sprite(Character) classes for Jumper game
from setting import *
import pygame as pyg
from os import path
from random import choice, randrange
vec = pyg.math.Vector2


game_folder = path.dirname(__file__)
data_folder = path.join(game_folder, "data")
char_folder = path.join(data_folder, "Base pack", "Player")

class Spritesheet:
    # Utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pyg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grab an image out of larger spritesheet
        image = pyg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        # gets the image and resize it for easy use
        image = pyg.transform.scale(image, (width//2, height//2))
        return image


class Player(pyg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]

        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT-100)
        self.pos = vec(40, HEIGHT-100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(color["black"])

        self.walking_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                                 self.game.spritesheet.get_image(692, 1458, 120, 207)]

        self.walking_frames_l = []
        for frame in self.walking_frames_r:
            frame.set_colorkey(color["black"])
            self.walking_frames_l.append(pyg.transform.flip(frame, True, False))

        self.jump_frame = self.game.spritesheet.get_image(416, 1660, 150, 181)
        self.jump_frame.set_colorkey(color["black"])

    # For a smaller jump
    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3
    # For a higher jump
    def jump(self):
        # jump only if
        self.rect.x += 2
        hits = pyg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pyg.key.get_pressed()
        if keys[pyg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pyg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # Apply friction to give character smooth movement
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Equation of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # Wrap around the screen so the player won't go out of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pyg.time.get_ticks()
        # If player horizontal velocity is not zero that must mean player is moving
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        # Show walk animation
        if self.walking:
            if now - self.last_update > 150:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                bottom = self.rect.bottom
                # If the velocity is increasing we use Right walk animation
                if self.vel.x > 0:
                    self.image = self.walking_frames_r[self.current_frame]
                # If velocity is decreasing we use Left walk animation
                else:
                    self.image = self.walking_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # Show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame+1)% len(self.standing_frames)
                # Last image bottom rect cordinates
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                # Locating it to new image bottom
                self.rect.bottom = bottom
        self.mask = pyg.mask.from_surface(self.image)

class Platform(pyg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.platforms
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        image = [self.game.spritesheet.get_image(0, 288, 380, 94),
                 self.game.spritesheet.get_image(213, 1662, 201, 100)]

        self.image = choice(image)
        self.image.set_colorkey(color["black"])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            Powerup(self.game, self)


class Powerup(pyg.sprite.Sprite):
    def __init__(self, game, plat):
        pyg.sprite.Sprite.__init__(self)
        self.groups = game.all_sprites, game.powerups
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(color["black"])
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()

class Mob(pyg.sprite.Sprite):
    def __init__(self, game):
        pyg.sprite.Sprite.__init__(self)
        self.groups = game.all_sprites, game.mobs
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(color["black"])
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(color["black"])
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT/2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0 :
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pyg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH +100 or self.rect.right < -100:
            self.kill()

class Cloud(pyg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites, game.clouds
        pyg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(color['black'])
        self.rect = self.image.get_rect()
        scale = randrange(50, 100)/100
        self.image = pyg.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, 50)

    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()