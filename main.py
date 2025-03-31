import pygame
import sys
import random
from collections import defaultdict

COLORS = {
    'background': (0, 0, 0),
    'text': (200, 200, 200),
    'button': (80, 80, 80),
    'text_field': (40, 40, 40),
    'active_field': (100, 100, 100),
    'rabbit': (220, 220, 220),
    'fox': (160, 60, 40)
}


class Rabbit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = 0
        self.max_age = random.randint(30, 40)
        self.breeding_cooldown = 0
        self.breeding_probability = 0.6
        self.min_breeding_age = 8


class Fox:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = 0
        self.max_age = random.randint(60, 80)
        self.hunting_cooldown = 10
        self.breeding_cooldown = 0  # Исправлено: добавлен атрибут
        self.breeding_probability = 0.4
        self.min_breeding_age = 10
        self.vision_radius = 12
        self.move_speed = 3
        self.breeding_interest = 0


class Simulation:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rabbits = []
        self.foxes = []

    def random_populate(self, rabbit_count, fox_count):
        for _ in range(rabbit_count):
            self.rabbits.append(Rabbit(
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            ))
        for _ in range(fox_count):
            self.foxes.append(Fox(
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            ))

    def tick(self):
        self.age_and_die()
        self.update_cooldowns()  # Добавлено обновление кулдаунов
        self.check_overcrowding()
        self.move_animals()
        self.hunt_rabbits()
        self.breed_animals()

    def update_cooldowns(self):
        for fox in self.foxes:
            if fox.breeding_cooldown > 0:
                fox.breeding_cooldown -= 1
            if fox.hunting_cooldown > 0:
                fox.hunting_cooldown -= 1

        for rabbit in self.rabbits:
            if rabbit.breeding_cooldown > 0:
                rabbit.breeding_cooldown -= 1

    def age_and_die(self):
        self.rabbits = [r for r in self.rabbits if r.age <= r.max_age]
        self.foxes = [f for f in self.foxes if f.age <= f.max_age]
        for animal in self.rabbits + self.foxes:
            animal.age += 1

    def check_overcrowding(self):
        for species in [self.rabbits, self.foxes]:
            death_list = set()
            for animal in species:
                count = sum(1 for other in species
                            if abs(other.x - animal.x) <= 40
                            and abs(other.y - animal.y) <= 40)
                if count > 50 and random.random() < 0.2:
                    death_list.add(animal)
            if species == self.rabbits:
                self.rabbits = [r for r in self.rabbits if r not in death_list]
            else:
                self.foxes = [f for f in self.foxes if f not in death_list]

    def move_animals(self):
        # Перемещение кроликов
        for rabbit in self.rabbits:
            nearby_foxes = [f for f in self.foxes
                            if abs(f.x - rabbit.x) <= 12
                            and abs(f.y - rabbit.y) <= 12]
            if nearby_foxes:
                dx = sum(rabbit.x - f.x for f in nearby_foxes)
                dy = sum(rabbit.y - f.y for f in nearby_foxes)
                dx = 2 if dx > 0 else -2
                dy = 2 if dy > 0 else -2
            else:
                dx, dy = random.choice([(-2, 0), (2, 0), (0, -2), (0, 2)])
            rabbit.x = max(0, min(self.width - 1, rabbit.x + dx))
            rabbit.y = max(0, min(self.height - 1, rabbit.y + dy))

        # Перемещение лис
        for fox in self.foxes:
            targets = [r for r in self.rabbits
                       if abs(r.x - fox.x) <= fox.vision_radius
                       and abs(r.y - fox.y) <= fox.vision_radius]
            if targets:
                target = random.choice(targets)
                dx = 1 if target.x > fox.x else -1
                dy = 1 if target.y > fox.y else -1
            else:
                dx, dy = random.choice([(-3, 0), (3, 0), (0, -3), (0, 3)])
            fox.x = max(0, min(self.width - 1, fox.x + dx))
            fox.y = max(0, min(self.height - 1, fox.y + dy))

    def hunt_rabbits(self):
        eaten = set()
        for fox in self.foxes:
            if fox.hunting_cooldown > 0:
                continue

            targets = [r for r in self.rabbits
                       if abs(r.x - fox.x) <= 2
                       and abs(r.y - fox.y) <= 2]
            if targets and random.random() < 0.7:
                eaten.update(random.sample(targets, min(2, len(targets))))
                fox.hunting_cooldown = 25
                fox.breeding_interest += 5
        self.rabbits = [r for r in self.rabbits if r not in eaten]

    def breed_animals(self):
        # Размножение кроликов
        rabbit_groups = defaultdict(list)
        for r in self.rabbits:
            rabbit_groups[(r.x, r.y)].append(r)
        new_rabbits = []
        for cell, group in rabbit_groups.items():
            eligible = [r for r in group
                        if r.breeding_cooldown == 0
                        and r.age >= r.min_breeding_age]
            if len(eligible) >= 2 and random.random() < 0.6:
                new_rabbits.append(Rabbit(cell[0], cell[1]))
                for r in eligible[:2]:
                    r.breeding_cooldown = 6
        self.rabbits.extend(new_rabbits)

        # Размножение лис
        fox_groups = defaultdict(list)
        for f in self.foxes:
            fox_groups[(f.x, f.y)].append(f)
        new_foxes = []
        for cell, group in fox_groups.items():
            eligible = [f for f in group
                        if f.breeding_interest > 0
                        and f.breeding_cooldown == 0
                        and f.age >= f.min_breeding_age]
            if len(eligible) >= 2 and random.random() < 0.4:
                new_foxes.append(Fox(cell[0], cell[1]))
                for f in eligible[:2]:
                    f.breeding_cooldown = 10
                    f.breeding_interest = 0
        self.foxes.extend(new_foxes)


class SimulationGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.state = "setup"
        self.simulation = None
        self.speed_factor = 3
        self.frame_counter = 0
        self.setup_state = {
            'rabbits': '',
            'foxes': '',
            'active_field': None
        }

    def draw_button(self, text, rect):
        pygame.draw.rect(self.screen, COLORS['button'], rect)
        text_surf = self.font.render(text, True, COLORS['text'])
        self.screen.blit(text_surf, (rect.x + 10, rect.y + 5))
        return rect.collidepoint(pygame.mouse.get_pos())

    def draw_text_field(self, text, rect, active=False):
        color = COLORS['active_field'] if active else COLORS['text_field']
        pygame.draw.rect(self.screen, color, rect)
        text_surf = self.font.render(text, True, COLORS['text'])
        self.screen.blit(text_surf, (rect.x + 10, rect.y + 5))

    def handle_setup_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if pygame.Rect(100, 100, 200, 30).collidepoint(mouse_pos):
                    self.setup_state['active_field'] = 'rabbits'
                elif pygame.Rect(100, 150, 200, 30).collidepoint(mouse_pos):
                    self.setup_state['active_field'] = 'foxes'
                elif pygame.Rect(100, 200, 200, 40).collidepoint(mouse_pos):
                    rabbits = int(self.setup_state['rabbits']) if self.setup_state['rabbits'] else 0
                    foxes = int(self.setup_state['foxes']) if self.setup_state['foxes'] else 0
                    self.simulation = Simulation(300, 300)
                    self.simulation.random_populate(rabbits, foxes)
                    self.state = 'simulation'
            if event.type == pygame.KEYDOWN and self.setup_state['active_field']:
                if event.key == pygame.K_BACKSPACE:
                    self.setup_state[self.setup_state['active_field']] = \
                        self.setup_state[self.setup_state['active_field']][:-1]
                elif event.unicode.isdigit():
                    self.setup_state[self.setup_state['active_field']] += event.unicode

    def draw_setup_screen(self):
        self.screen.fill(COLORS['background'])
        self.draw_text_field(f"Rabbits: {self.setup_state['rabbits']}",
                             pygame.Rect(100, 100, 200, 30),
                             self.setup_state['active_field'] == 'rabbits')
        self.draw_text_field(f"Foxes: {self.setup_state['foxes']}",
                             pygame.Rect(100, 150, 200, 30),
                             self.setup_state['active_field'] == 'foxes')
        self.draw_button("Start Simulation", pygame.Rect(100, 200, 200, 40))

    def draw_simulation(self):
        self.screen.fill(COLORS['background'])
        for r in self.simulation.rabbits:
            pygame.draw.circle(self.screen, COLORS['rabbit'], (r.x * 2, r.y * 2), 2)
        for f in self.simulation.foxes:
            pygame.draw.circle(self.screen, COLORS['fox'], (f.x * 2, f.y * 2), 2)

        text = self.font.render(f"Rabbits: {len(self.simulation.rabbits)}", True, COLORS['text'])
        self.screen.blit(text, (610, 10))
        text = self.font.render(f"Foxes: {len(self.simulation.foxes)}", True, COLORS['text'])
        self.screen.blit(text, (610, 40))

    def run(self):
        while True:
            if self.state == "setup":
                self.draw_setup_screen()
                self.handle_setup_events()
            elif self.state == "simulation":
                self.frame_counter += 1
                if self.frame_counter % self.speed_factor == 0:
                    self.simulation.tick()
                    self.frame_counter = 0
                self.draw_simulation()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    gui = SimulationGUI()
    gui.run()