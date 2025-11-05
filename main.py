import random
from pathlib import Path

from objects import Passenger, Station, Train, Line
from log import Logger
from tsp import solve_tsp_cycle


class World:
    __STATION_SHAPE_TYPE = ['circle', 'triangle', 'square']
    __OPTION = ['add_passenger', 'add_line','add_bridge', 'update_station']

    def __init__(
        self,
        init_stations: int,
        init_trains: int,
        init_lines: int,
        init_passengers: int,
        gen_station_interval: int,
        gen_train_interval: int,
        gen_passenger_interval: int,
    ):
        self._clock = 0
        self._stations = {}
        self._trains = {}
        self._lines = {}
        self._passengers = {}

        self._gen_station_interval = gen_station_interval
        self._gen_train_interval = gen_train_interval
        self._gen_passenger_interval = gen_passenger_interval

        # generate initial stations
        for i in range(init_stations):
            station = self.generate_staion()
            self._stations[station.name] = station

        # generate initial trains
        for i in range(init_trains):
            train = self.generate_train()
            self._trains[train.name] = train

        # generate initial lines
        for i in range(init_lines):
            line = self.generate_line()
            self._lines[line.name] = line

        # generate initial passengers
        for i in range(init_passengers):
            passenger = self.generate_passenger()
            self._passengers[passenger.name] = passenger

    @property
    def clock(self):
        return self._clock

    @property
    def station_dict(self):
        return self._stations

    @property
    def train_dict(self):
        return self._trains

    @property
    def line_dict(self):
        return self._lines

    @property
    def passenger_dict(self):
        return self._passengers

    def step(self):
        # count clock
        self._clock += 1

        # generate station
        if self._clock % self._gen_station_interval == 0:
            station = self.generate_staion()
            self._stations[station.name] = station
        # generate train
        if self._clock % self._gen_train_interval == 0:
            train = self.generate_train()
            self._trains[train.name] = train
        # generate passenger
        if self._clock % self._gen_passenger_interval == 0:
            passenger = self.generate_passenger()
            self._passengers[passenger.name] = passenger

        # update traion location
        for line in self._lines.values():
            line.step(self.passenger_dict)

    def reset(self, new_clock: int):
        self._clock = new_clock

    def generate_staion(self):
        index = len(self._stations)
        name = f'station_{index}'
        shape_type = random.choice(World.__STATION_SHAPE_TYPE)
        x_coord = random.random()
        y_coord = random.random()
        print(f'generate: {name} ({shape_type}) at ({x_coord}, {y_coord})')
        return Station(name, shape_type, x_coord, y_coord)

    def generate_train(self):
        index = len(self._trains)
        name = f'train_{index}'
        print(f'generate: {name}')
        return Train(name)

    def generate_line(self):
        index = len(self._lines)
        name = f'line_{index}'
        print(f'generate: {name}')
        return Line(name)

    def generate_passenger(self):
        index = len(self._passengers)
        name = f'passenger_{index}'
        shape_type = random.choice(World.__STATION_SHAPE_TYPE)
        candidate_stations = [
            station.name for station in self._stations.values()
            if station.shape_type != shape_type
        ]
        current_location = random.choice(candidate_stations)
        print(f'generate: {name} ({shape_type}) at {current_location} for ...')
        return Passenger(name, shape_type, current_location, 'to_be')


# Lineが1本の場合のPlyer
class Player:
    def __init__(
        self,
        world,
        line_opt_interval,
        train_opt_interval,
    ):
        self._world = world
        self._line_opt_interval = line_opt_interval
        self._train_opt_interval = train_opt_interval

        stations = self._world.station_dict
        trains = self._world.train_dict
        lines = self._world.line_dict

        assert len(trains) == 1
        assert len(lines) == 1

        # connect stations with initial line
        line = list(lines.values())[0]
        for key, val in stations.items():
            line.add_station(key, val)
        
        # add train to initial line
        train = list(trains.values())[0]
        line.add_train(train.name, train)

    def step(self):
        if self._world.clock % self._line_opt_interval == 0:
            # add new stations into line_0
            line = list(self._world.line_dict.values())[0]
            for key, val in self._world.station_dict.items():
                if not key in line.station_dict:
                    line.add_station(key, val)
            tour_keys, length = solve_tsp_cycle(line.station_dict)
            line.reorder_staions(tour_keys)
        
        if self._world.clock % self._train_opt_interval == 0:
            # add new trains into line_0
            line = list(self._world.line_dict.values())[0]
            for key, val in self._world.train_dict.items():
                if not key in line.train_dict:
                    line.add_train(key, val)


def main():
    # get output dir
    index = 0
    while 1:
        path = Path(f'./out/run_{index}')
        if path.exists():
            index += 1
        else:
            path.mkdir(parents=True, exist_ok=True)
            break

    # initialize world
    world = World(
        init_stations=3,
        init_trains=1,
        init_lines=1,
        init_passengers=0,
        gen_station_interval=100,
        gen_train_interval=500,
        gen_passenger_interval=10,
    )

    # initialize player
    player = Player(
        world=world,
        line_opt_interval=100,
        train_opt_interval=100,
    )

    logger = Logger(
        world=world,
        path=path/'log.json'
    )

    # start simulation
    for i in range(1000):
        world.step()
        player.step()
        logger.save()

    print(f'stations   : {len(world.station_dict.keys())}')
    print(f'trains     : {len(world.train_dict.keys())}')
    print(f'lines      : {len(world.line_dict.keys())}')
    for name, line in world.line_dict.items():
        print(f'  {name}.stations => {list(line.station_dict.keys())}')
        print(f'  {name}.trains   => {list(line.train_dict.keys())}')
    print(f'passengers : {len(world.passenger_dict.keys())}')
    print(f'program terminated.')

if __name__ == "__main__":
    main()