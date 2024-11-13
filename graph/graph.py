from typing import List, Tuple, Dict
import math

class Sensor:
    def __init__(self, identifier: int, position: Tuple[float, float], range_radius: float, is_base_station: bool = False):
        self.identifier = identifier
        self.position = position
        self.range_radius = range_radius
        self.is_base_station = is_base_station
    
    def distance_to(self, other_sensor: 'Sensor') -> float:
        x1, y1 = self.position
        x2, y2 = other_sensor.position
        euclidian_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return euclidian_distance
    
    def can_communicate_with(self, other_sensor: 'Sensor') -> bool:
        return self.distance_to(other_sensor) <= self.range_radius

class SensorNetwork:
    def __init__(self):
        self.sensors: Dict[int, Sensor] = {}
        self.adjacency_matrix: List[List[float]] = []
        self.qtd_sensors = 0

    def add_sensor(self, sensor: Sensor):
        id = sensor.identifier
        self.sensors[id] = sensor

    def load_from_file(self, file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if i == 0:
                num_sensors = int(line.strip())
                self.qtd_sensors = num_sensors
            elif i == 1:
                base_station_coords = tuple(map(float, line.strip().split(',')))
                sensor = Sensor(identifier=0, position=base_station_coords, range_radius=100.0, is_base_station=True)
                self.add_sensor(sensor)
            else:
                x, y = map(float, line.strip().split(','))
                sensor = Sensor(identifier=i-1, position=(x, y), range_radius=100.0)
                self.add_sensor(sensor)
        
        self.qtd_sensors = len(self.sensors)
        print(self.qtd_sensors)

        self.build_adjacency_matrix()

    def build_adjacency_matrix(self):
        size = len(self.sensors)
        self.adjacency_matrix = [[float('inf')] * size for _ in range(size)]

        for sensor_1_id in self.sensors:
            sensor1 = self.sensors[sensor_1_id]

            for sensor_2_id in self.sensors:
                sensor2 = self.sensors[sensor_2_id]

                if sensor_1_id != sensor_2_id:
                    distance = sensor1.distance_to(sensor2)
                    if sensor1.can_communicate_with(sensor2):
                        self.adjacency_matrix[sensor_1_id][sensor_2_id] = distance
                    else:
                        self.adjacency_matrix[sensor_1_id][sensor_2_id] = float('inf')
                else:
                    self.adjacency_matrix[sensor_1_id][sensor_2_id] = 0.0
    
    def print_adjacency_matrix(self) -> None:
        for i in range(self.qtd_sensors):
            for j in range(self.qtd_sensors):
                print(f"{self.adjacency_matrix[i][j]: .2f}", end="\t")
            print()


if __name__ == "__main__":
    file_path = "data/Cenário 4 - Rede 50.txt"
    graph = SensorNetwork()
    graph.load_from_file(file_path)
    graph.print_adjacency_matrix()