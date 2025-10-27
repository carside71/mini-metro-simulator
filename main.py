import sys
import os
import random
from typing import Optional

from tsp import solve_tsp_cycle


class Passenger:
    def __init__(
        self,
        name: str,
        shape_type: str,
        current_location: str,
        distination: str,
    ):
        self._name = name
        self._shape_type = shape_type
        self._current_location = current_location
        self._distination = distination

    @property
    def name(self):
        return self._name

    @property
    def shape_type(self):
        return self._shape_type

    @property
    def current_location(self):
        return self._current_location

    @property
    def distination(self):
        return self._distination

    def update_current_location(self, new_location: str):
        self._current_location = new_location

    def update_distination(self, new_distination: str):
        self._distination = new_distination


class Station:
    def __init__(
        self,
        name: str,
        shape_type: str,
        x_coord: float,
        y_coord: float,
    ):
        self._name = name
        self._shape_type = shape_type
        self._x_coord = x_coord
        self._y_coord = y_coord

    @property
    def name(self):
        return self._name

    @property
    def x(self):
        return self._x_coord

    @property
    def y(self):
        return self._y_coord

    @property
    def shape_type(self):
        return self._shape_type


class Train:
    def __init__(
        self,
        name: str,
        x_coord: Optional[float] = None,
        y_coord: Optional[float] = None,
    ):
        self._name = name
        self._x_coord = x_coord
        self._y_coord = y_coord

    @property
    def name(self):
        return self._name

    @property
    def x(self):
        return self._x_coord

    @property
    def y(self):
        return self._y_coord

    def update_coords(self, x_coord: float, y_coord: float):
        self._x_coord = x_coord
        self._y_coord = y_coord


class Line:
    def __init__(
        self,
        name: str,
        station_dict: dict = {},
        train_dict: dict = {},
        connection_list: list = [],
    ):
        self._name = name
        self._stations = station_dict
        self._trains = train_dict

    @property
    def name(self):
        return self._name

    @property
    def station_dict(self):
        return self._stations

    @property
    def train_dict(self):
        return self._trains

    def add_station(self, name, station):
        self._stations[name] = station

    def add_train(self, name, train):
        self._trains[name] = train

    def remove_station(self, name: str):
        del self._stations[name]
        print(f'remove station {name} from {self._name}')
        for station in self._stations.keys():
            if station != name:
                self.remove_connection(name, station)

    def remove_train(self, name: str):
        del self._trains[name]
        print(f'remove train {name} from {self._name}')


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

    def reset(self, new_clock: int):
        self._clock = new_clock

    def generate_staion(self):
        index = len(self._stations)
        name = f'station_{index}'
        shape_tpye = random.choice(World.__STATION_SHAPE_TYPE)
        x_coord = random.random()
        y_coord = random.random()
        print(f'generate: {name} ({shape_tpye}) at ({x_coord}, {y_coord})')
        return Station(name, shape_tpye, x_coord, y_coord)

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
        shape_tpye = random.choice(World.__STATION_SHAPE_TYPE)
        current_location = random.choice([*self._stations.keys()])
        print(f'generate: {name} ({shape_tpye}) at {current_location} for ...')
        return Passenger(name, shape_tpye, current_location, 'to_be')


class Player:
    def __init__(
        self,
        world,
        opt_interval,
    ):
        self._world = world
        self._opt_interval = opt_interval

        # connect stations with initial line
        stations = self._world.station_dict
        line = list(self._world.line_dict.values())[0]
        self.add_stations_into_a_line(line, stations)

    def step(self):
        if self._world.clock % self._opt_interval == 0:
            # connect stations with initial line
            stations = self._world.station_dict
            line = list(self._world.line_dict.values())[0]
            self.add_stations_into_a_line(line, stations)

    def add_stations_into_a_line(self, line: Station, stations: dict):
        tour_keys, length = solve_tsp_cycle(stations)
        for name in tour_keys:
            line.add_station(name, stations[name])


def main():
    # initialize world
    world = World(
        init_stations=3,
        init_trains=1,
        init_lines=1,
        init_passengers=0,
        gen_station_interval=1000,
        gen_train_interval=5000,
        gen_passenger_interval=100,
    )

    # initialize player
    player = Player(
        world=world,
        opt_interval=5000,
    )

    # start simulation
    for i in range(10000):
        world.step()
        player.step()

    print(f'stations   : {len(world.station_dict.keys())}')
    print(f'trains     : {len(world.train_dict.keys())}')
    print(f'lines      : {len(world.line_dict.keys())}')
    for name, line in world.line_dict.items():
        print(f'  {name} => {line.station_dict.keys()}')
    print(f'passengers : {len(world.passenger_dict.keys())}')
    print(f'program terminated.')

if __name__ == "__main__":
    main()