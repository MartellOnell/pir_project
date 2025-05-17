import pygame
import sys
import random
from collections import defaultdict
import time
import pprint
import json

from config import SimulationSettings, SimulationStatusChoices
from graphics import StatisticsStorage

from settings_interface_main import SettingsFrame
import subprocess

COLORS = {
    'background': (0, 0, 0),
    'text': (200, 200, 200),
    'button': (80, 80, 80),
    'text_field': (40, 40, 40),
    'active_field': (100, 100, 100),
    'rabbit': (220, 220, 220),
    'fox': (160, 60, 40),
    'bush': (0,128,0),
}


class Bush:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.current_regrowth = 0
        # костыль ибо я не хочу лезть в логику
        self.berries = 0
        self.__is_berries_called = False
    
    # не постоянные переменные, которые можно поменять
    @property
    def berries(self):
        if self.__is_berries_called:
            return self.__berries
        else:
            self.__berries = random.randint(
                SimulationSettings().get_attr('berries_random_from'),
                SimulationSettings().get_attr('berries_random_to'),
            )
            self.__is_berries_called = True

            return self.__berries
        
    @berries.setter
    def berries(self, value):
        self.__is_berries_called = True
        self.__berries = value

    @property
    def regrowth_time(self):
        return SimulationSettings().get_attr('berries_regrowth_time')

    def take_berry(self):
        if self.berries > 0:
            self.berries -= 1
            return True
        return False

    def update(self):
        if self.berries < SimulationSettings().get_attr('berries_random_to'):
            self.current_regrowth += 1
            if self.current_regrowth >= self.regrowth_time:
                self.berries += 1
                self.current_regrowth = 0


class Rabbit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = 0
        self.breeding_cooldown = 0
        # костыль ибо я не хочу лезть в логику
        self.__max_age = 0

    
    # не постоянные переменные, которые можно поменять
    @property
    def max_age(self):
        if self.__max_age != 0:
            return self.__max_age
        else:
            self.__max_age = random.randint(
                SimulationSettings().get_attr('rabbit_max_age_random_from'),
                SimulationSettings().get_attr('rabbit_max_age_random_to'),
            )

            return self.__max_age

    @property
    def min_breeding_age(self):
        return SimulationSettings().get_attr('rabbit_min_breeding_age')
    
    @property
    def breeding_probability(self):
        return SimulationSettings().get_attr('rabbit_breeding_probability')
    
    @property
    def vision_radius(self):
        return SimulationSettings().get_attr('rabbit_vision_radius')


class Fox:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = 0
        self.hunger = 0
        self.hunting_cooldown = 10
        self.breeding_cooldown = 0
        self.breeding_interest = 0
        # костыль ибо я не хочу лезть в логику
        self.__max_age = 0

    # не постоянные переменные, которые можно поменять
    @property
    def max_age(self):
        if self.__max_age != 0:
            return self.__max_age
        else:
            self.__max_age = random.randint(
                SimulationSettings().get_attr('fox_max_age_random_from'),
                SimulationSettings().get_attr('fox_max_age_random_to'),
            )

            return self.__max_age
        
    @property
    def breeding_probability(self):
        return SimulationSettings().get_attr('fox_breeding_probability')
        
    @property
    def min_breeding_age(self):
        return SimulationSettings().get_attr('fox_min_breeding_age')
        
    @property
    def move_speed(self):
        return SimulationSettings().get_attr('fox_move_speed')
        
    @property
    def vision_radius(self):
        return SimulationSettings().get_attr('fox_vision_radius')


class Simulation:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rabbits = []
        self.foxes = []
        self.bushes = []

    def random_populate(self, rabbit_count: int, fox_count: int, bush_count: int):
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
        for _ in range(bush_count):
            self.bushes.append(Bush(
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            ))

    def tick(self):
        self.age_and_die()
        self.update_cooldowns()  # Добавлено обновление кулдаунов
        self.check_overcrowding()
        self.move_animals()
        self.hunt_rabbits()
        self.eat_berries()  # Новая функция
        self.breed_animals()
        self.update_bushes()  # Новая функция
        StatisticsStorage().add_data(
            data_type='r',
            value=len(self.rabbits),
        )
        StatisticsStorage().add_data(
            data_type='f',
            value=len(self.foxes),
        )


    def update_bushes(self):
        for bush in self.bushes:
            bush.update()

    def eat_berries(self):
        for fox in self.foxes:
            if fox.hunger > 50 and random.random() < 0.3:
                nearby_bushes = [b for b in self.bushes
                                if abs(b.x - fox.x) <= 5
                                and abs(b.y - fox.y) <= 5]
                for bush in nearby_bushes:
                    if bush.take_berry():
                        fox.hunger = max(0, fox.hunger - 30)
                        break

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
                            if abs(f.x - rabbit.x) <= rabbit.vision_radius
                            and abs(f.y - rabbit.y) <= rabbit.vision_radius]
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
                dx = random.randint(1, 3) if target.x > fox.x else -random.randint(1, 3)
                dy = random.randint(1, 3) if target.y > fox.y else -random.randint(1, 3)
            else:
                dx, dy = random.choice(
                    [
                        (-fox.move_speed, 0),
                        (fox.move_speed, 0),
                        (0, -fox.move_speed),
                        (0, fox.move_speed),
                    ]
                )
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


class NakedSimulationRunner:
    def __init__(self):
        self.config = SimulationSettings()
        self.simulation = Simulation(300, 300)
        self.simulation.random_populate(
            rabbit_count=self.config.get_attr("rabbit_amount"),
            fox_count=self.config.get_attr("fox_amount"),
            bush_count=self.config.get_attr("bush_amount"),
        )

    @property
    def statistics_template(self):
        return '\r----------\nstatistic: \nrabbits: {0}\nfoxes: {1}\nticks: {2}\nbushes: {3}\n----------'

    def get_statistics(self, tick_counter: int = 0):
        sys.stdout.write(
            self.statistics_template.format(
                len(self.simulation.rabbits),
                len(self.simulation.foxes),
                tick_counter,
                len(self.simulation.bushes),
            ),
        )

    def run(self):
        tick_counter: int = 0
        sys.stdout.write('starting simulation')
        time.sleep(3)

        while True:
            tick_counter += 1
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            self.simulation.tick()
            # кейс когда один вид вымирает и мы завершаем симуляцию
            if len(self.simulation.rabbits) == 0 or len(self.simulation.foxes) == 0:
                self.get_statistics(tick_counter)
                pprint.pp(StatisticsStorage().get_statistics())
                sys.stdout.write('\nsimulation finished')
                break

        # боже прости меня ибо я согрешил, но я рот ебал этого ткинтера
        data_to_subprocess = json.dumps(StatisticsStorage().get_statistics())
        subprocess_script: str = (
            "from graphics import plot_statistics; "
            "data = {0}; "
            "plot_statistics(data)".format(data_to_subprocess)
        )
        subprocess.run(
            [
                "python", 
                "-c",
                subprocess_script,
            ]
        )


class SimulationGUI:
    def __init__(self):
        pygame.init()
        self.simulation = Simulation(300, 300)
        self.simulation.random_populate(
            rabbit_count=SimulationSettings().get_attr("rabbit_amount"),
            fox_count=SimulationSettings().get_attr("fox_amount"),
            bush_count=SimulationSettings().get_attr("bush_amount"),
        )
        self.screen = pygame.display.set_mode((900, 600))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.speed_factor = 3
        self.frame_counter = 0

    @property
    def state(self):
        return SimulationSettings().get_attr('status')


    def draw_simulation(self):
        self.screen.fill(COLORS['background'])
        for r in self.simulation.rabbits:
            pygame.draw.circle(self.screen, COLORS['rabbit'], (r.x * 2, r.y * 2), 2)
        for f in self.simulation.foxes:
            pygame.draw.circle(self.screen, COLORS['fox'], (f.x * 2, f.y * 2), 2)
        for b in self.simulation.bushes:
            pygame.draw.circle(self.screen, COLORS['bush'], (b.x * 2, b.y * 2), 2)

        text = self.font.render(f"Rabbits: {len(self.simulation.rabbits)}", True, COLORS['text'])
        self.screen.blit(text, (610, 10))
        text = self.font.render(f"Foxes: {len(self.simulation.foxes)}", True, COLORS['text'])
        self.screen.blit(text, (610, 40))
        text = self.font.render(f"Bushes: {len(self.simulation.bushes)}", True, COLORS['text'])
        self.screen.blit(text, (610, 70))

    def run(self):
        while True:
            if self.state == SimulationStatusChoices.SIMULATION:
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

    settings_frame = SettingsFrame()
    settings_frame.mainloop()

    if SimulationSettings().get_attr('status') == SimulationStatusChoices.SIMULATION:
        print('chosen simulation')
        gui = SimulationGUI()
        gui.run()
    elif SimulationSettings().get_attr('status') == SimulationStatusChoices.NAKED_SIMULATION:
        print('chosen naked simulation')
        NakedSimulationRunner().run()