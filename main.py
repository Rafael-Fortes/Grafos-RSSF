import pygame
from typing import Tuple

from core.graph import SensorNetwork, Sensor
from core.simulation import Simulation

class Screen:
    def __init__(self, width: int, height: int, bg_color: Tuple[int, int, int], simulation: Simulation):
        pygame.init()
        pygame.display.set_caption("Rede de Sensores Sem Fio")

        self.screen = pygame.display.set_mode((width, height))
        self.bg_color = bg_color
        self.clock = pygame.time.Clock()
        self.running = True
        self.simulation = simulation
        self.display_radius = False
        self.display_paths = False

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.simulation.create_new_simulation("data/Cenário 4 - Rede 400.txt", 100, "minimum_spanning_tree_prim")
                if event.key == pygame.K_SPACE:
                    self.simulation.run_simulation(1)
                if event.key == pygame.K_DELETE:
                    self.simulation.delete_simulation()
                if event.key == pygame.K_r:
                    self.display_radius = not self.display_radius
                if event.key == pygame.K_p:
                    self.display_paths = not self.display_paths

    def update(self):
        # Atualizações futuras (e.g., simulação de sensores) serão feitas aqui.
        pass

    def draw(self):
        self.screen.fill(self.bg_color)
        self.draw_communication_lines()
        self.draw_paths()
        self.draw_sensors()
        pygame.display.flip()
    
    def draw_sensors(self):
        if self.simulation.network is None:
            return
        
        for sensor_id in self.simulation.network.sensors:
            sensor = self.simulation.network.sensors[sensor_id]

            if sensor.is_base_station:
                base_station = sensor

            if not sensor.is_base_station:
                x, y = sensor.position
                screen_x = int(round((x / 1000) * self.screen.get_width()))
                screen_y = int(round((y / 1000) * self.screen.get_height()))
                battery_level = sensor.battery

                # Desenhar o raio de alcance
                if self.display_radius:
                    range_radius_on_screen = int(round((sensor.range_radius / 1000) * self.screen.get_width()))
                    pygame.draw.circle(self.screen, (0, 0, 255), (screen_x, screen_y), range_radius_on_screen, 1)

                # Desenhar o sensor
                if battery_level >= 0.750:
                    red = 0
                    green = 255
                    blue = 0
                elif battery_level >= 0.500:
                    red = 255
                    green = 255
                    blue = 0
                elif battery_level >= 0:
                    red = 255
                    green = 165
                    blue = 0
                else:
                    red = 255
                    green = 0
                    blue = 0
            
                sensor_color = (red, green, blue)
                pygame.draw.circle(self.screen, sensor_color, (screen_x, screen_y), 10)

        x, y = base_station.position
        screen_x = int(round((x / 1000) * self.screen.get_width()))
        screen_y = int(round((y / 1000) * self.screen.get_height()))
        pygame.draw.circle(self.screen, (0, 0, 255), (screen_x, screen_y), 8)
    
    def draw_paths(self):
        if self.simulation.network is None or not self.display_paths:
            return
        for sensor_id in self.simulation.current_paths:
            path = self.simulation.current_paths[sensor_id]
            visited = set()

            for i in range(len(path)):
                if i == 0:
                    continue
                
                if (path[i - 1], path[i]) in visited:
                    continue

                sensor1 = self.simulation.network.sensors[path[i - 1]]
                sensor2 = self.simulation.network.sensors[path[i]]
                visited.add((sensor1.identifier, sensor2.identifier))

                x1, y1 = sensor1.position
                x2, y2 = sensor2.position
                screen_x1 = int(round((x1 / 1000) * self.screen.get_width()))
                screen_y1 = int(round((y1 / 1000) * self.screen.get_height()))
                screen_x2 = int(round((x2 / 1000) * self.screen.get_width()))
                screen_y2 = int(round((y2 / 1000) * self.screen.get_height()))
                pygame.draw.line(self.screen, (0, 0, 0), (screen_x1, screen_y1), (screen_x2, screen_y2), 1)
        
    
    def draw_communication_lines(self):
        if self.simulation.network is None or self.display_paths:
            return
        
        for sensor_1_id in range(self.simulation.network.qtd_sensors):
            sensor1 = self.simulation.network.sensors[sensor_1_id]

            for sensor_2_id in range(self.simulation.network.qtd_sensors):
                sensor2 = self.simulation.network.sensors[sensor_2_id]

                if sensor1.can_communicate_with(sensor2):
                    x1, y1 = sensor1.position
                    x2, y2 = sensor2.position
                    screen_x1 = int(round((x1 / 1000) * self.screen.get_width()))
                    screen_y1 = int(round((y1 / 1000) * self.screen.get_height()))
                    screen_x2 = int(round((x2 / 1000) * self.screen.get_width()))
                    screen_y2 = int(round((y2 / 1000) * self.screen.get_height()))
                    pygame.draw.line(self.screen, (0, 0, 0), (screen_x1, screen_y1), (screen_x2, screen_y2), 1)

    def __del__(self):
        pygame.quit()

if __name__ == "__main__":
    qtd_sensors = 400
    dataset_path = f"data/Cenário 4 - Rede {qtd_sensors}.txt"

    simulation = Simulation()

    visualizer = Screen(width=600, height=600, bg_color=(255, 255, 255), simulation=simulation)
    visualizer.run()