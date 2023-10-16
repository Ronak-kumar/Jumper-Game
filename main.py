import random
import pygame.display
import pygame.font
import pygame.image
import pygame.mixer
import pygame.sprite
from sprites import *


class Game:
    def __init__(self):
        # initialize game window, etc.
        pyg.init()
        pyg.mixer.init()
        self.screen = pyg.display.set_mode((WIDTH, HEIGHT))
        pyg.display.set_caption(TITTLE)
        self.clock = pyg.time.Clock()
        self.running = True
        self.font_name_1 = pyg.font.match_font("verdana")
        self.font_name_2 = pyg.font.match_font("georgia")
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        self.img_dir = path.join(self.dir, "Jumper_Data")
        with open(path.join(self.dir, HS_FILE), "r") as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(self.img_dir, SPRITESHEET))

        # Cloud images
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pyg.image.load(path.join(self.img_dir, f"cloud{i}.png".format(i))).convert())

        # load sound
        self.snd_dir = path.join(self.dir, "Game_Sound")
        self.jump_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'Jump10.wav'))
        self.boost_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'Powerup7.wav'))



    def new(self):
        # Starts a new game
        self.score = 0
        self.all_sprites = pyg.sprite.Group()
        self.platforms = pyg.sprite.Group()
        self.powerups = pyg.sprite.Group()
        self.mobs = pyg.sprite.Group()
        self.clouds = pyg.sprite.Group()
        self.mob = Mob(self)
        self.player = Player(self)
        for plat in PLAYER_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        pyg.mixer.music.load(path.join(self.snd_dir, 'Happy Tune.wav'))
        self.run()

    def run(self):
        # Game loop
        pyg.mixer.music.play(loops = -1)
        self.playing = True
        while self.playing:
            # this confirms that the loop have completed under 0.03 second
            # And if it had completed before 0.3 second then it will wait till the times up and then run next loop
            # so that it will run at the same speed
            self.clock.tick(FPS)
            # Processing input (events)
            self.events()
            # To update the sprites after meeting a certain condition
            self.update()
            # Draw / Render
            self.draw()
        pyg.mixer.music.fadeout(500)

    def update(self):
        # Game loop - update
        # To update the sprites after meeting a certain condition in the next frame
        self.all_sprites.update()

        # spqwn a mob
        now = pyg.time.get_ticks()
        if now - self.mob_timer > 10000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)

        # hit mobs?
        # If hit mobs game will end
        # For pixel perfect collision we are using pygame_mask function
        mob_hits = pyg.sprite.spritecollide(self.player, self.mobs, False, pyg.sprite.collide_mask)
        if mob_hits:
            self.playing = False

        # check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pyg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest_plat = hits[0]
                # Collecting the lowest platform in the collision.
                # If collision is happening with more than one platform
                for hit in hits:
                    if hit.rect.bottom > lowest_plat.rect.bottom:
                        lowest_plat = hit

                # Checking whether the player are out of the platform or not
                if self.player.pos.x < lowest_plat.rect.right + 7 and \
                    self.player.pos.x > lowest_plat.rect.left - 7:
                    # If the player feet get on the platform ony then he can land on it
                    if self.player.pos.y < lowest_plat.rect.centery:
                        self.player.pos.y = hits[0].rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False

        # if player reaches top 1/4 of the screen
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100)<15:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y/2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # If a player hits a powerup
        pow_hits = pyg.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in pow_hits:
            if powerup.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = - BOOST_POWER
                self.player.jumping = False


        # If player hits bottom of the screen (Die!)
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
            if len(self.platforms) == 0:
                self.playing = False


        # Spawn new platform to keep same average number
        while len(self.platforms) < 6:
            width = random.randint(50, 150)
            x = random.randint(0, WIDTH-width)
            y = random.randint(-75, -30)
            p = Platform(self, x, y)
            self.platforms.add(p)
            self.all_sprites.add(p)


    def events(self):
        # Game loop - events
        # Processing input (events)
        for event in pyg.event.get():
            # Check for closing window
            if event.type == pyg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_SPACE:
                    self.player.jump()

            if event.type == pyg.KEYUP:
                if event.key == pyg.K_SPACE:
                    self.player.jump_cut()


    def draw(self):
        # Game loop - draw
        # To drawing updated frame on the screen
        self.screen.fill(BGCOLOR)
        # To draw all the updated sprites
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.screen.blit(self.mob.image, self.mob.rect)
        self.draw_text((f"Score: {self.score}"), self.font_name_2, 23, color["white"], 60, 15)
        if self.score > self.highscore:
            self.draw_text(f"High Score: {self.score}", self.font_name_2, 23, color["white"], WIDTH - 90, 15)
        else :
            self.draw_text(f"High Score: {self.highscore}", self.font_name_2, 23, color["white"], WIDTH-90, 15)
        # After drawing everything flip the display
        pyg.display.flip()

    def show_start_screen(self):
        # Game splash / Start screen
        self.background("splash.jpeg")

        # Initializing game start music
        pyg.mixer.music.load(path.join(self.snd_dir, 'Yippee.wav'))
        pyg.mixer.music.play(loops = -1)

        #self.screen.fill(BGCOLOR)
        self.draw_text(TITTLE, self.font_name_2, 55, color["white"], WIDTH/2, HEIGHT/4)
        self.draw_text("Arrows to move Space to jump", self.font_name_2, 25, color["white"], WIDTH/2, HEIGHT/2)
        self.draw_text("Press any key to play", self.font_name_2, 25, color["black"], WIDTH/2, HEIGHT*3/4+30)
        self.draw_text(f"High Score: {self.highscore}", self.font_name_2, 25, color["white"], WIDTH/2, 15)
        pyg.display.flip()
        self.wait_for_key()
        pyg.mixer_music.fadeout(500)

    def background(self, image):
        # Changing start/end screen background
        self.image = path.join(self.img_dir, image)
        bg = pygame.image.load(self.image)
        bg = pyg.transform.scale(bg, (WIDTH, HEIGHT))
        self.screen.blit(bg, (0, 0))

    def show_go_screen(self):

        # Game over / Continue screen


        if not self.running:
            return

        # Initializing game ending music
        pyg.mixer.music.load(path.join(self.snd_dir, 'prologue.mp3'))
        pyg.mixer.music.play(loops=-1)
        self.background("end.jpeg")
        #self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", self.font_name_2, 60, color["white"], WIDTH / 2, HEIGHT / 4)
        self.draw_text(f"Your Score: {self.score}", self.font_name_2, 25, color["white"], WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to play again", self.font_name_2, 25, color["white"], WIDTH / 2, HEIGHT * 3 / 4+30)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", self.font_name_2, 25, color["red"], WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), "w") as f:
                f.write(str(self.score))
        else:
            self.draw_text(f"High Score: {self.highscore} ", self.font_name_2, 25, color["red"], WIDTH / 2, HEIGHT / 2 + 40)

        pyg.display.flip()
        self.wait_for_key()
        pyg.mixer_music.fadeout(500)



    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pyg.KEYUP:
                    waiting = False

    def draw_text(self, text, font_style, size, color, x, y):
        font = pygame.font.Font(font_style, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_go_screen()

    pyg.quit()
