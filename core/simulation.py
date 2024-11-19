from core.graph import SensorNetwork, Sensor
from typing import Dict, List, Tuple

class Simulation:
    def __init__(self):
        self.network: SensorNetwork = None
        self.current_paths: Dict[int, list] = {}
    
    def create_new_simulation(self, dataset_path: str, epochs: int, algorithm: str) -> bool:
        print("Criando nova simulação...")
        self.epochs = epochs
        self.current_epoch = 0
        self.network = SensorNetwork()
        self.algorithm = algorithm
        
        try:
            self.network.load_from_file(dataset_path)
        except FileNotFoundError:
            print("Dataset não encontrado.")
            return False

        print("Simulação criada com sucesso.")
        return True

    def delete_simulation(self) -> None:
        self.network = None
        print("Simulação deletada.")

    def next_step(self) -> Dict[int, List[int]]:
        self.current_epoch += 1
        self.current_paths: Dict[int, list] = {}

        self.network.remove_depleted_sensors()

        for sensor_id in range(1, self.network.qtd_sensors):
            path = self.network.get_shortest_path(sensor_id, 0, self.algorithm)
            self.current_paths[sensor_id] = path
            self.network.simulate_data_transmission(sensor_id, 0, path)
        
        return self.current_paths
