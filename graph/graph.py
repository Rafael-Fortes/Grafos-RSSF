from typing import List, Tuple, Dict, Optional
import math
import heapq

class Sensor:
    def __init__(self, identifier: int, position: Tuple[float, float], range_radius: float, battery_capacity: float, is_base_station: bool = False):
        self.identifier = identifier
        self.position = position
        self.range_radius = range_radius
        self.battery = battery_capacity
        self.is_base_station = is_base_station
    
    def distance_to(self, other_sensor: 'Sensor') -> float:
        x1, y1 = self.position
        x2, y2 = other_sensor.position
        euclidian_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return euclidian_distance
    
    def can_communicate_with(self, other_sensor: 'Sensor') -> bool:
        return self.distance_to(other_sensor) <= self.range_radius
    
    def consume_energy_for_transmission(self, energy: float) -> bool:
        if self.battery >= energy:
            self.battery -= energy
            return True
        return False

    def consume_energy_for_reception(self, energy: float) -> bool:
        if self.battery >= energy:
            self.battery -= energy
            return True
        return False

class SensorNetwork:
    def __init__(self):
        self.sensors: Dict[int, Sensor] = {}
        self.transmission_matrix: List[List[float]] = []
        self.reception_matrix: List[List[float]] = []
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
                sensor = Sensor(identifier=0, position=base_station_coords, range_radius=100.0, battery_capacity=float('inf'), is_base_station=True)
                self.add_sensor(sensor)
            else:
                x, y = map(float, line.strip().split(','))
                sensor = Sensor(identifier=i-1, position=(x, y), range_radius=100.0, battery_capacity=1000.0)
                self.add_sensor(sensor)
        
        self.qtd_sensors = len(self.sensors)
        self.build_adjacency_matrix()

    def build_adjacency_matrix(self):
        size = len(self.sensors)
        self.transmission_matrix = [[float('inf')] * size for _ in range(size)]
        self.reception_matrix = [[float('inf')] * size for _ in range(size)]

        # Parâmetros para cálculo de energia
        Eelec = 50e-9  # Energia consumida pela eletrônica de transmissão e recepção (em joules por bit)
        Eamp = 100e-12  # Energia consumida pelo amplificador (em joules por bit por metro quadrado)
        k = 4000  # Número de bits transmitidos e recebidos

        for sensor_1_id in self.sensors:
            sensor1 = self.sensors[sensor_1_id]

            for sensor_2_id in self.sensors:
                sensor2 = self.sensors[sensor_2_id]

                if sensor_1_id != sensor_2_id:
                    distance = sensor1.distance_to(sensor2)
                    if sensor1.can_communicate_with(sensor2):
                        # Calcular a energia necessária para a transmissão
                        transmission_energy = Eelec * k + Eamp * k * distance**2
                        self.transmission_matrix[sensor_1_id][sensor_2_id] = transmission_energy
                        
                        # Calcular a energia necessária para a recepção
                        reception_energy = Eelec * k
                        self.reception_matrix[sensor_1_id][sensor_2_id] = reception_energy
                    else:
                        self.transmission_matrix[sensor_1_id][sensor_2_id] = float('inf')
                        self.reception_matrix[sensor_1_id][sensor_2_id] = float('inf')
                else:
                    self.transmission_matrix[sensor_1_id][sensor_2_id] = 0.0
                    self.reception_matrix[sensor_1_id][sensor_2_id] = 0.0

    def print_adjacency_matrices(self) -> None:
        print("Transmission Energy Matrix:")
        for i in range(self.qtd_sensors):
            for j in range(self.qtd_sensors):
                print(f"{self.transmission_matrix[i][j]: .2e}", end="\t")
            print()

        print("\nReception Energy Matrix:")
        for i in range(self.qtd_sensors):
            for j in range(self.qtd_sensors):
                print(f"{self.reception_matrix[i][j]: .2e}", end="\t")
            print()
    
        
    def simulate_communication(self, sender_id: int, receiver_id: int, k: int) -> Optional[float]:
        transmission_energy = self.transmission_matrix[sender_id][receiver_id]
        reception_energy = self.reception_matrix[sender_id][receiver_id]

        sender = self.sensors[sender_id]
        receiver = self.sensors[receiver_id]

        if sender.battery > transmission_energy and receiver.battery > reception_energy:
            if sender.consume_energy_for_transmission(transmission_energy) and receiver.consume_energy_for_reception(reception_energy):
                print(f"Communication successful between Sensor {sender_id} and Sensor {receiver_id}")
                return transmission_energy + reception_energy
            else:
                print(f"Communication failed between Sensor {sender_id} and Sensor {receiver_id} due to insufficient battery.")
                return None
    
    def simulate_data_transmission(self, start_id: int, end_id: int) -> Optional[float]:
        path = self.get_shortest_path(start_id, end_id)
        total_energy = 0.0
        
        if not path:
            print(f"No path found from sensor {start_id} to sensor {end_id}.")
            return None

        for i in range(len(path) - 1):
            sender = path[i]
            receiver = path[i + 1]

            result = self.simulate_communication(sender, receiver, 4000)
            if result is None:
                print(f"Communication failed between Sensor {sender} and Sensor {receiver}.")
                return None
            
            total_energy += result
        print(f"Data successfully transmitted from sensor {start_id} to sensor {end_id}.")
        return total_energy

    def dijkstra(self, start_id: int) -> Tuple[Dict[int, float], Dict[int, int]]:
        distances = {sensor_id: float('inf') for sensor_id in self.sensors}
        previous_nodes = {sensor_id: None for sensor_id in self.sensors}
        distances[start_id] = 0

        priority_queue = [(0, start_id)]

        while priority_queue:
            current_distance, current_id = heapq.heappop(priority_queue)

            if current_distance > distances[current_id]:
                continue

            for neighbor_id, energy_cost in enumerate(self.transmission_matrix[current_id]):
                if energy_cost < float('inf'):  # Verifica se há uma ligação válida
                    distance = current_distance + energy_cost

                    if distance < distances[neighbor_id]:
                        distances[neighbor_id] = distance
                        previous_nodes[neighbor_id] = current_id
                        heapq.heappush(priority_queue, (distance, neighbor_id))

        return distances, previous_nodes

    def get_shortest_path(self, start_id: int, end_id: int) -> List[int]:
        distances, previous_nodes = self.dijkstra(start_id)
        path = []
        current_id = end_id

        while current_id is not None:
            path.insert(0, current_id)
            current_id = previous_nodes[current_id]

        if distances[end_id] < float('inf'):
            return path
        else:
            return []


if __name__ == "__main__":
    file_path = "data/Cenário 4 - Rede 400.txt"
    graph = SensorNetwork()
    graph.load_from_file(file_path)
    # graph.print_adjacency_matrices()
    print(graph.get_shortest_path(399, 0))
    total_energy = graph.simulate_data_transmission(399, 0)
    print(f"Sensor 399 battery: {graph.sensors[399].battery}")
    print(f"Sensor 0 battery: {graph.sensors[0].battery}")
    print(f"Toal energy consumed: {total_energy}")