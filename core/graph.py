from random import randint
from random import uniform

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
        euclidian_distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) # revisão
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
    
    def can_transmit(self, energy: float) -> bool:
        return self.battery >= energy
    
    def can_receive(self, energy: float) -> bool:
        return self.battery >= energy

class SensorNetwork:
    def __init__(self):
        self.sensors: Dict[int, Sensor] = {}
        self.transmission_matrix: List[List[float]] = []
        self.reception_matrix: List[List[float]] = []
        self.qtd_sensors = 0

    def add_sensor(self, sensor: Sensor):
        id = sensor.identifier
        self.sensors[id] = sensor

    def load_from_file(self, file_path: str) -> bool:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if i == 0:
                self.qtd_sensors = int(line.strip())
            elif i == 1:
                base_station_coords = tuple(map(float, line.strip().split(',')))
                sensor = Sensor(identifier=0, position=base_station_coords, range_radius=100.0, battery_capacity=float('inf'), is_base_station=True)
                self.add_sensor(sensor)
            else:
                battery = 0.5
                x, y = map(float, line.strip().split(','))
                sensor = Sensor(identifier=i-1, position=(x, y), range_radius=100.0, battery_capacity=battery)
                self.add_sensor(sensor)
        
        if self.qtd_sensors != len(self.sensors) - 1:
            # print("Erro ao carregar os sensores.")
            self.sensors = {}
            self.qtd_sensors = 0
            return False

        self.qtd_sensors = len(self.sensors)
        self.build_adjacency_matrix()
        return True

    def build_adjacency_matrix(self, Eelec: float = 50e-9, Eamp: float = 100e-12, k: int = 4000) -> None:
        size = len(self.sensors)

        self.transmission_matrix = [[float('inf')] * size for _ in range(size)]
        self.reception_matrix = [[float('inf')] * size for _ in range(size)]

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

    # def print_adjacency_matrices(self) -> None:
        # print("Matriz de gasto energético para transmissão:")
        for i in range(self.qtd_sensors):
            for j in range(self.qtd_sensors):
                # print(f"{self.transmission_matrix[i][j]: .2e}", end="\t")
            # print()

        # print("\nMatriz de gasto energético para recepção:")
        for i in range(self.qtd_sensors):
            for j in range(self.qtd_sensors):
                # print(f"{self.reception_matrix[i][j]: .2e}", end="\t")
            # print()
    
        
    def simulate_communication(self, sender_id: int, receiver_id: int, k: int) -> Optional[float]:
        if receiver_id not in self.sensors or sender_id not in self.sensors:
            return None
        
        transmission_energy = self.transmission_matrix[sender_id][receiver_id]
        reception_energy = self.reception_matrix[sender_id][receiver_id]


        sender = self.sensors[sender_id]
        receiver = self.sensors[receiver_id]

        if sender.battery > transmission_energy and receiver.battery > reception_energy:
            if sender.consume_energy_for_transmission(transmission_energy) and receiver.consume_energy_for_reception(reception_energy):
                total_energy = transmission_energy + reception_energy
                # print(f"Comunicação realizada com sucesso entre sensor {sender_id} e o sensor {receiver_id}. Consumo total de energia: {total_energy}")
                return total_energy
            else:
                # print(f"Comunicação falhou entre o sensor {sender_id} e o sensor {receiver_id} por falta de bateria.")
                return None
    
    def dijkstra(self, start_id: int) -> Tuple[Dict[int, float], Dict[int, int]]:
        distances = {sensor_id: float('inf') for sensor_id in self.sensors}
        previous_nodes = {sensor_id: None for sensor_id in self.sensors}
        distances[start_id] = 0

        priority_queue = [(0, start_id)]

        while priority_queue:
            current_distance, current_id = heapq.heappop(priority_queue)

            if current_distance > distances[current_id]:
                continue

            current_sensor = self.sensors[current_id]

            for neighbor_id, energy_cost in enumerate(self.transmission_matrix[current_id]):
                neighbor_sensor = self.sensors[neighbor_id]
                receive_cost = self.reception_matrix[current_id][neighbor_id]

                if energy_cost < float('inf'):
                    distance = current_distance + energy_cost

                    if distance < distances[neighbor_id]:
                        distances[neighbor_id] = distance
                        previous_nodes[neighbor_id] = current_id
                        heapq.heappush(priority_queue, (distance, neighbor_id))

        return distances, previous_nodes
    
    def minimum_spanning_tree_prim(self, start_id: int = 0) -> Tuple[Dict[int, Optional[int]], float]:
        visited = [False] * self.qtd_sensors
        predecessors = {sensor_id: None for sensor_id in self.sensors}
        min_edge_cost = [float('inf')] * self.qtd_sensors
        min_edge_cost[start_id] = 0
        total_cost = 0

        priority_queue = [(0, start_id)]

        while priority_queue:
            current_cost, current_id = heapq.heappop(priority_queue)

            if visited[current_id]:
                continue

            visited[current_id] = True
            total_cost += current_cost

            for neighbor_id, weight in enumerate(self.transmission_matrix[current_id]):
                if not visited[neighbor_id] and weight < min_edge_cost[neighbor_id]:
                    min_edge_cost[neighbor_id] = weight
                    predecessors[neighbor_id] = current_id
                    heapq.heappush(priority_queue, (weight, neighbor_id))

        return total_cost, predecessors


    def get_shortest_path(self, start_id: int, end_id: int, type_algorithm: str = 'dijkstra') -> List[int]:
        if type_algorithm == 'dijkstra':
            distances, previous_nodes = self.dijkstra(start_id)
        
        if type_algorithm == 'minimum_spanning_tree_prim':
            distances, previous_nodes = self.minimum_spanning_tree_prim(start_id)
        path = []
        current_id = end_id

        while current_id is not None:
            path.insert(0, current_id)
            current_id = previous_nodes[current_id]

        # if distances[end_id] < float('inf'):
        #     return path
        # else:
        #     return []

        if len(path) == 1:
            # print(f"Sensor {start_id} e Sensor {end_id} não estão conectados.")
            return []
        else:
            # print(f"Menor caminho entre Sensor {start_id} e Sensor {end_id}: {path}. Distância: {distances[end_id]}")
            return path
    
    def simulate_data_transmission(self, start_id: int, end_id: int, path: str) -> Optional[float]:
        total_energy = 0.0

        # Itera sobre o caminho, simulando a comunicação entre sensores
        for i in range(len(path) - 1):
            sender = path[i]
            receiver = path[i + 1]

            # Simula a comunicação e calcula o consumo de energia
            result = self.simulate_communication(sender, receiver, 4000)  # Supondo que 4000 seja o tamanho dos dados
            if result is None:
                # print(f"Comunicação entre sensor {sender} e sensor {receiver} falhou.")
                return None
            
            # Atualiza o total de energia consumida
            total_energy += result

            # Atualiza a energia do sensor de envio
            self.sensors[sender].battery -= result  # Subtrai o consumo de energia do sensor sender

            # Verifica se o sensor ficou sem energia
            if self.sensors[sender].battery <= 0:
                return None  

        # Se todos os sensores estiverem bem, retorna o total de energia consumida
        # print(f"Os dados foram transmitidos com sucesso de {start_id} para {end_id}. Gastou-se {total_energy} de energia.")
        return total_energy

    
    def select_random_sensor(self) -> int:
        sensor_ids = list(self.sensors.keys())
        sensor_ids.remove(0)
        return sensor_ids[randint(0, len(sensor_ids) - 1)]

    def run_simulation_agm(self, max_rounds: int = 400, algorithm: str = 'minimum_spanning_tree_prim'):
        for round_num in range(max_rounds):
            # print(f"\n--- Round {round_num + 1} ---")

            start_sensor = self.select_random_sensor()
            end_sensor = 0

            path = self.get_shortest_path(start_sensor, end_sensor, algorithm)
            if not path:
                # print("No path found. Rebuilding the network...")
                _, _ = self.minimum_spanning_tree_prim()
                continue

            total_energy = self.simulate_data_transmission(start_sensor, end_sensor, algorithm)

            if total_energy is None:
                # print("Energy depleted on one or more sensors. Rebuilding the network...")
                self.remove_depleted_sensors()
                _, _ = self.minimum_spanning_tree_prim()
            else:
                # print(f"Round {round_num + 1} completed successfully.")
                # print(f"total energy: {total_energy}")
                # print(f"path: {path}")
        
    def run_simulation_djikstra(self, algorithm: str = 'dijkstra'):
        for i in range(1, self.qtd_sensors):
            start = i
            end = 0

            # print(self.get_shortest_path(start, end, algorithm))
            total_energy = self.simulate_data_transmission(start, end, algorithm)

            # print(f"Sensor {start} battery: {self.sensors[start].battery}")
            # print(f"Toal energy consumed: {total_energy}")

    def remove_depleted_sensors(self):
        sensors_to_remove = []

        for sensor_id, sensor in self.sensors.items():
            if sensor.battery <= 0:
                # print(f"Removendo {sensor_id} devido a bateria esgotada.")
                sensors_to_remove.append(sensor_id)
        
        for sensor_id in sensors_to_remove:
            for neighbor_id in range(self.qtd_sensors):
                self.transmission_matrix[sensor_id][neighbor_id] = float('inf')
                self.transmission_matrix[neighbor_id][sensor_id] = float('inf')

                self.reception_matrix[sensor_id][neighbor_id] = float('inf')
                self.reception_matrix[neighbor_id][sensor_id] = float('inf')




if __name__ == "__main__":
    file_path = "data/Cenário 4 - Rede 400.txt"
    graph = SensorNetwork()
    graph.load_from_file(file_path)
    graph.print_adjacency_matrices()

    graph.run_simulation_agm()
    #graph.run_simulation_djikstra()

    