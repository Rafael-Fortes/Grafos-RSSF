from typing import Tuple
import math

class Sensor:
    def __init__(self, identifier: str, position: Tuple[int, int], range_radius: float):
        self.identifier = identifier
        self.position = position
        self.range_radius = range_radius
    
    def distance_to(self, other_sensor: 'Sensor') -> float:
        x1, y1 = self.position
        x2, y2 = other_sensor.position
        return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
    
    def can_communicate_with(self, other_sensor: 'Sensor') -> bool:
        return self.distance_to(other_sensor) <= self.range_radius


class SensorNetwork:
    def __init__(self):
        self.sensors = []

    def add_sensor(self, sensor: Sensor):
        self.sensors.append(sensor)
    
    def load_from_file(self, file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        num_sensors = int(lines[0].strip())
        base_station_coords = tuple(map(float, lines[1].strip().split(',')))
        self.base_station = Sensor(identifier="Base", position=base_station_coords, range_radius=0)

        for i in range(2, 2 + num_sensors):
            x, y = map(float, lines[i].strip().split(','))
            sensor = Sensor(identifier=str(i-2), position=(x, y), range_radius=100.0)
            self.add_sensor(sensor)

    def get_communication_pairs(self):
        pairs = []
        for i, sensor in enumerate(self.sensors):
            for other_sensor in self.sensors[i+1:]:
                if sensor.can_communicate_with(other_sensor):
                    pairs.append((sensor, other_sensor))
        return pairs