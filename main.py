import pygame
from typing import Tuple

from graph.graph import SensorNetwork

class Screen:
    def __init__(self, width: int, height: int, bg_color: Tuple[int, int, int], sensor_network: SensorNetwork):
        pygame.init()
        pygame.display.set_caption("Rede de Sensores Sem Fio")

        self.screen = pygame.display.set_mode((width, height))
        self.bg_color = bg_color
        self.clock = pygame.time.Clock()
        self.running = True
        self.sensor_network = sensor_network

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

    def update(self):
        # Atualizações futuras (e.g., simulação de sensores) serão feitas aqui.
        pass

    def draw(self):
        self.screen.fill(self.bg_color)
        self.draw_communication_lines()
        self.draw_sensors()
        # Métodos para desenhar nós e arestas serão chamados aqui.
        pygame.display.flip()
    
    def draw_sensors(self):
        for sensor_id in self.sensor_network.sensors:
            sensor = self.sensor_network.sensors[sensor_id]
            x, y = sensor.position
            screen_x = int(round((x / 1000) * self.screen.get_width()))
            screen_y = int(round((y / 1000) * self.screen.get_height()))

            # Desenhar o raio de alcance
            # range_radius_on_screen = int(round((sensor.range_radius / 1000) * self.screen.get_width()))
            # pygame.draw.circle(self.screen, (0, 0, 255), (screen_x, screen_y), range_radius_on_screen, 1)

            # Desenhar o sensor
            pygame.draw.circle(self.screen, (0, 0, 255), (screen_x, screen_y), 5)

            if sensor.is_base_station:
                base_station = sensor

        x, y = base_station.position
        screen_x = int(round((x / 1000) * self.screen.get_width()))
        screen_y = int(round((y / 1000) * self.screen.get_height()))
        pygame.draw.circle(self.screen, (255, 0, 0), (screen_x, screen_y), 8)
    
    def draw_communication_lines(self):
        for sensor_1_id in range(self.sensor_network.qtd_sensors):
            sensor1 = self.sensor_network.sensors[sensor_1_id]

            for sensor_2_id in range(self.sensor_network.qtd_sensors):
                sensor2 = self.sensor_network.sensors[sensor_2_id]

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

    sensor_network = SensorNetwork()
    sensor_network.load_from_file(dataset_path)

    visualizer = Screen(width=600, height=600, bg_color=(255, 255, 255), sensor_network=sensor_network)
    visualizer.run()