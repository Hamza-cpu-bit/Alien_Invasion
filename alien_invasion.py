import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Get screen info for responsive design
info = pygame.display.Info()
SCREEN_WIDTH = min(1200, info.current_w - 100)
SCREEN_HEIGHT = min(800, info.current_h - 100)

# Colors
BLACK = (10, 10, 26)
WHITE = (255, 255, 255)
GREEN = (0, 255, 136)
RED = (255, 68, 68)
BLUE = (0, 136, 255)
YELLOW = (255, 220, 0)
CYAN = (0, 255, 255)
PURPLE = (200, 0, 255)

# Game settings
FPS = 60


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 6
        self.color = GREEN
        self.health = 3
        self.max_health = 3
        self.shield_active = False
        self.shield_timer = 0
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shoot_cooldown = 0

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

    def update(self):
        if self.shield_timer > 0:
            self.shield_timer -= 1
            self.shield_active = True
        else:
            self.shield_active = False

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
            self.rapid_fire = True
        else:
            self.rapid_fire = False

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, screen):
        # Draw shield
        if self.shield_active:
            pygame.draw.circle(screen, CYAN,
                               (int(self.x + self.width // 2), int(self.y + self.height // 2)),
                               35, 3)

        # Draw ship body (triangle)
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)

        # Draw engines
        pygame.draw.rect(screen, RED, (self.x + 8, self.y + self.height - 10, 8, 15))
        pygame.draw.rect(screen, RED, (self.x + self.width - 16, self.y + self.height - 10, 8, 15))

    def shoot(self):
        cooldown = 5 if self.rapid_fire else 15
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = cooldown
            return True
        return False


class Bullet:
    def __init__(self, x, y, direction=1, color=YELLOW, speed=8):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 15
        self.speed = speed * direction
        self.color = color
        self.active = True

    def update(self):
        self.y -= self.speed
        if self.y < -20 or self.y > SCREEN_HEIGHT + 20:
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


class Alien:
    def __init__(self, x, y, alien_type=0):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.type = alien_type
        self.colors = [RED, PURPLE, BLUE]
        self.color = self.colors[alien_type % 3]
        self.points = (alien_type + 1) * 10
        self.active = True
        self.shoot_cooldown = random.randint(0, 120)

    def update(self, direction, speed):
        self.x += direction * speed
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def can_shoot(self):
        return self.shoot_cooldown <= 0 and random.random() < 0.02

    def shoot(self):
        self.shoot_cooldown = random.randint(60, 180)

    def draw(self, screen):
        # Draw alien body
        pygame.draw.rect(screen, self.color, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))

        # Draw eyes
        pygame.draw.circle(screen, WHITE, (int(self.x + 12), int(self.y + 15)), 5)
        pygame.draw.circle(screen, WHITE, (int(self.x + 23), int(self.y + 15)), 5)
        pygame.draw.circle(screen, BLACK, (int(self.x + 12), int(self.y + 15)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + 23), int(self.y + 15)), 3)

        # Draw antennae
        pygame.draw.line(screen, self.color, (self.x + 10, self.y + 5), (self.x + 5, self.y - 5), 2)
        pygame.draw.line(screen, self.color, (self.x + 25, self.y + 5), (self.x + 30, self.y - 5), 2)


class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = power_type  # 'health', 'shield', 'rapid_fire'
        self.speed = 2
        self.active = True
        self.colors = {'health': GREEN, 'shield': CYAN, 'rapid_fire': YELLOW}
        self.color = self.colors[power_type]

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)

        # Draw icon
        font = pygame.font.Font(None, 24)
        icons = {'health': 'H', 'shield': 'S', 'rapid_fire': 'R'}
        text = font.render(icons[self.type], True, WHITE)
        screen.blit(text, (self.x + 8, self.y + 6))


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / 30))
            color = tuple([min(255, c + alpha // 3) for c in self.color])
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Alien Invasion")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 80)
        self.bullets = []
        self.alien_bullets = []
        self.aliens = []
        self.powerups = []
        self.particles = []

        self.score = 0
        self.level = 1
        self.wave = 1
        self.alien_direction = 1
        self.alien_speed = 1
        self.aliens_move_down = False
        self.move_down_amount = 0

        self.game_state = 'menu'  # menu, playing, paused, game_over
        self.high_score = 0

        self.spawn_aliens()

    def spawn_aliens(self):
        rows = 3 + self.level // 2
        cols = 6 + self.level // 3
        spacing = 60
        start_x = (SCREEN_WIDTH - (cols * spacing)) // 2
        start_y = 50

        for row in range(rows):
            for col in range(cols):
                alien = Alien(start_x + col * spacing, start_y + row * spacing, row % 3)
                self.aliens.append(alien)

    def create_explosion(self, x, y, color):
        for _ in range(20):
            self.particles.append(Particle(x, y, color))

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if self.game_state == 'playing':
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move(-1)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move(1)
            if keys[pygame.K_SPACE]:
                if self.player.shoot():
                    bullet = Bullet(self.player.x + self.player.width // 2 - 2, self.player.y)
                    self.bullets.append(bullet)

    def update(self):
        if self.game_state != 'playing':
            return

        self.player.update()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        for bullet in self.alien_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.alien_bullets.remove(bullet)

        # Update aliens
        move_down = False
        edge_reached = False

        for alien in self.aliens:
            alien.update(self.alien_direction, self.alien_speed)

            if alien.x <= 0 or alien.x >= SCREEN_WIDTH - alien.width:
                edge_reached = True

            if alien.can_shoot():
                alien.shoot()
                bullet = Bullet(alien.x + alien.width // 2, alien.y + alien.height, -1, RED, 5)
                self.alien_bullets.append(bullet)

        if edge_reached:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien.y += 20

        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update()
            if not powerup.active:
                self.powerups.remove(powerup)

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Check collisions
        self.check_collisions()

        # Check win condition
        if not self.aliens:
            self.level += 1
            self.wave += 1
            self.alien_speed += 0.3
            self.spawn_aliens()

        # Check loss condition
        for alien in self.aliens:
            if alien.y + alien.height >= self.player.y:
                self.game_state = 'game_over'
                return

        if self.player.health <= 0:
            self.game_state = 'game_over'

    def check_collisions(self):
        # Player bullets vs aliens
        for bullet in self.bullets[:]:
            for alien in self.aliens[:]:
                if (bullet.x < alien.x + alien.width and
                        bullet.x + bullet.width > alien.x and
                        bullet.y < alien.y + alien.height and
                        bullet.y + bullet.height > alien.y):

                    self.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    self.score += alien.points
                    self.create_explosion(alien.x + alien.width // 2, alien.y + alien.height // 2, alien.color)

                    # Spawn power-up chance
                    if random.random() < 0.15:
                        power_type = random.choice(['health', 'shield', 'rapid_fire'])
                        self.powerups.append(PowerUp(alien.x, alien.y, power_type))
                    break

        # Alien bullets vs player
        for bullet in self.alien_bullets[:]:
            if (bullet.x < self.player.x + self.player.width and
                    bullet.x + bullet.width > self.player.x and
                    bullet.y < self.player.y + self.player.height and
                    bullet.y + bullet.height > self.player.y):

                self.alien_bullets.remove(bullet)
                if not self.player.shield_active:
                    self.player.health -= 1
                    self.create_explosion(self.player.x + self.player.width // 2,
                                          self.player.y + self.player.height // 2, RED)

        # Power-ups vs player
        for powerup in self.powerups[:]:
            if (powerup.x < self.player.x + self.player.width and
                    powerup.x + powerup.width > self.player.x and
                    powerup.y < self.player.y + self.player.height and
                    powerup.y + powerup.height > self.player.y):

                self.powerups.remove(powerup)

                if powerup.type == 'health':
                    self.player.health = min(self.player.max_health, self.player.health + 1)
                elif powerup.type == 'shield':
                    self.player.shield_timer = 300
                elif powerup.type == 'rapid_fire':
                    self.player.rapid_fire_timer = 300

    def draw(self):
        self.screen.fill(BLACK)

        # Draw stars
        for i in range(100):
            x = (i * 123) % SCREEN_WIDTH
            y = (i * 456) % SCREEN_HEIGHT
            brightness = 100 + (i * 17) % 156
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), 1)

        if self.game_state == 'menu':
            self.draw_menu()
        elif self.game_state == 'playing':
            self.draw_game()
        elif self.game_state == 'paused':
            self.draw_game()
            self.draw_paused()
        elif self.game_state == 'game_over':
            self.draw_game()
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self):
        title = self.font.render("ALIEN INVASION", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        instructions = [
            "Press SPACE to Start",
            "",
            "Controls:",
            "Arrow Keys / A,D - Move",
            "SPACE - Shoot",
            "P - Pause",
            "ESC - Menu",
            "",
            "Power-ups:",
            "H - Extra Health",
            "S - Shield",
            "R - Rapid Fire"
        ]

        y = SCREEN_HEIGHT // 2
        for instruction in instructions:
            text = self.small_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 30

    def draw_game(self):
        # Draw game objects
        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for bullet in self.alien_bullets:
            bullet.draw(self.screen)

        for alien in self.aliens:
            alien.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        # Draw HUD
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 40))

        # Draw health
        for i in range(self.player.health):
            pygame.draw.polygon(self.screen, RED, [
                (SCREEN_WIDTH - 40 - i * 35, 20),
                (SCREEN_WIDTH - 50 - i * 35, 35),
                (SCREEN_WIDTH - 30 - i * 35, 35)
            ])

        # Draw active power-ups
        y_offset = 70
        if self.player.shield_active:
            shield_text = self.small_font.render(f"Shield: {self.player.shield_timer // 60}s", True, CYAN)
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 25

        if self.player.rapid_fire:
            rapid_text = self.small_font.render(f"Rapid Fire: {self.player.rapid_fire_timer // 60}s", True, YELLOW)
            self.screen.blit(rapid_text, (10, y_offset))

    def draw_paused(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        text = self.font.render("PAUSED", True, YELLOW)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        resume = self.small_font.render("Press P to Resume", True, WHITE)
        resume_rect = resume.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(resume, resume_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        level_text = self.small_font.render(f"Reached Level: {self.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(level_text, level_rect)

        restart = self.small_font.render("Press SPACE to Restart", True, GREEN)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart, restart_rect)

        menu = self.small_font.render("Press ESC for Menu", True, WHITE)
        menu_rect = menu.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        self.screen.blit(menu, menu_rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == 'playing':
                            self.game_state = 'menu'
                        elif self.game_state == 'game_over':
                            self.reset_game()

                    if event.key == pygame.K_SPACE:
                        if self.game_state == 'menu':
                            self.game_state = 'playing'
                        elif self.game_state == 'game_over':
                            self.reset_game()
                            self.game_state = 'playing'

                    if event.key == pygame.K_p:
                        if self.game_state == 'playing':
                            self.game_state = 'paused'
                        elif self.game_state == 'paused':
                            self.game_state = 'playing'

            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()