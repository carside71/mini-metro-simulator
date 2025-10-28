import sys
import os
import math
import random
from pathlib import Path
from typing import Optional
from collections import Counter

from tsp import solve_tsp_cycle
from log import Logger


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
        current_station: Optional[Station] = None,
        next_station: Optional[Station] = None,
    ):
        self._name = name
        self._x_coord = x_coord
        self._y_coord = y_coord
        self._current_station = current_station
        self._next_station = next_station

        # set train distination vector
        if isinstance(current_station, Station) and isinstance(next_station, Station):
            self.set_dist_vector(current_station, next_station)
        else:
            self._dist_vector_x = None
            self._dist_vector_y = None

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
    def dist_vector_x(self):
        return self._dist_vector_x

    @property
    def dist_vector_y(self):
        return self._dist_vector_y

    @property
    def current_station(self):
        return self._current_station

    @property
    def next_station(self):
        return self._next_station

    def update_coords(self, x_coord: float, y_coord: float):
        self._x_coord = x_coord
        self._y_coord = y_coord

    def set_stations(self, current_station: Station, next_station: Station):
        self._current_station = current_station
        self._next_station = next_station
        self.update_coords(current_station.x, current_station.y)
        self.set_dist_vector(current_station, next_station)
        print(f'set {self.name} at ({self.x}, {self.y}) [{self.current_station.name} - {self.next_station.name}]')

    def set_dist_vector(self, current_station: Station, next_station: Station):
        vec_x = next_station.x - current_station.x
        vec_y = next_station.y - current_station.y
        norm = math.sqrt(vec_x**2 + vec_y**2)
        self._dist_vector_x = vec_x / norm
        self._dist_vector_y = vec_y / norm


class Line:
    def __init__(
        self,
        name: str,
        station_dict: dict = {},
        train_dict: dict = {},
        train_step: float = 0.01,
    ):
        self._name = name
        self._stations = station_dict
        self._trains = train_dict
        self._train_step = train_step

    @property
    def name(self):
        return self._name

    @property
    def station_dict(self):
        return self._stations

    @property
    def train_dict(self):
        return self._trains

    @property
    def train_step(self):
        return self._train_step

    def step(self):
        for train in self.train_dict.values():
            x_new = train.x + self.train_step * train.dist_vector_x
            y_new = train.y + self.train_step * train.dist_vector_y
            if (train.next_station.x < train.x) == (train.next_station.x < x_new):
                train.update_coords(x_new, y_new)
            else:
                print(f'reached {train.name} to {train.next_station.name} from {train.current_station.name}')
                train.update_coords(train.next_station.x, train.next_station.y)
                # update current/next station of train
                station_name_list = list(self.station_dict.keys())
                idx = station_name_list.index(train.next_station.name)
                if idx + 1 < len(station_name_list):
                    name = station_name_list[idx + 1]
                else:
                    name = station_name_list[0]
                new_next_station = self.station_dict[name]
                train.set_stations(train.next_station, new_next_station)

    def reorder_staions(self, key_list: list):
        if not Counter(key_list) == Counter(self._stations.keys()):
            raise RuntimeError
        new_stations = {}
        for key in key_list:
            if key in self._stations:
                new_stations[key] = self._stations[key]
        self._stations = new_stations

    def add_station(self, name, station):
        self._stations[name] = station

    def add_train(self, name, train):
        self._trains[name] = train
        if len(self._stations) < 2:
            raise RuntimeError
        current_station = list(self._stations.values())[0]
        next_station = list(self._stations.values())[1]
        train.set_stations(current_station, next_station)

    def remove_station(self, name: str):
        del self._stations[name]
        print(f'remove station {name} from {self._name}')

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

        # update traion location
        for line in self._lines.values():
            line.step()

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