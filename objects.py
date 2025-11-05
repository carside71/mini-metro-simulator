import math
from typing import Optional
from collections import Counter

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

    def update_current_location(self, new_location: str):
        self._current_location = new_location


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
    __TRAIN_STATUS = ['move', 'stop', 'none']  # 移動中、停車中、線路に乗っていない
    def __init__(
        self,
        name: str,
        status: str = 'none',
        speed_coeff: float = 2.0,
        x_coord: Optional[float] = None,
        y_coord: Optional[float] = None,
        current_station: Optional[Station] = None,
        next_station: Optional[Station] = None,
    ):
        assert status in Train.__TRAIN_STATUS
        self._name = name
        self._status = status
        self._speed_coeff = speed_coeff
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
    def status(self):
        return self._status

    @property
    def speed_coeff(self):
        return self._speed_coeff

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

    def set_status(self, status: str):
        assert status in Train.__TRAIN_STATUS
        self._status = status

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
        self._dist_vector_x = self.speed_coeff * vec_x / norm
        self._dist_vector_y = self.speed_coeff * vec_y / norm


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

    def step(self, passengers: dict):
        # 電車の位置更新or乗客の乗り降りを各電車で実行
        for train in self.train_dict.values():
            if train.status == 'move':
                x_new = train.x + self.train_step * train.dist_vector_x
                y_new = train.y + self.train_step * train.dist_vector_y
                if (train.next_station.x < train.x) == (train.next_station.x < x_new):
                    train.update_coords(x_new, y_new)
                else:
                    print(f'reached {train.name} to {train.next_station.name} from {train.current_station.name}')
                    train.update_coords(train.next_station.x, train.next_station.y)
                    train.set_status('stop')
            elif train.status == 'stop':
                # 電車に乗っている乗客を取得 -> List[Passenger]
                train_name = train.name
                passengers_in_train = [
                    passenger for passenger in passengers.values()
                    if passenger.current_location == train_name
                ]
                # 電車の乗客のうち、この駅で降りる乗客を取得 -> List[Passenger]
                station_shape_type = train.next_station.shape_type
                passengers_to_getoff = [
                    passenger for passenger in passengers_in_train
                    if passenger.shape_type == station_shape_type
                ]
                # 降りる乗客がいなければ駅からの乗車処理に進む、いれば先頭の乗客を削除する
                if len(passengers_to_getoff) != 0:
                    # 先頭の乗客の現在地を更新
                    passengers_to_getoff[0].update_current_location('none')
                else:
                    # この路線のすべての駅タイプを取得 -> List[str]
                    staion_shape_types_in_line = [
                        station.shape_type for station in self._stations.values()
                    ]
                    # 停車中の駅にいる乗客を取得 -> List[Passenger]
                    station_name = train.next_station.name
                    passengers_in_station = [
                        passenger for passenger in passengers.values()
                        if passenger.current_location == station_name
                    ]
                    # 駅の乗客のうち、この路線で目的地まで運べる乗客を取得 -> List[Passenger]
                    passengers_to_pickup = [
                        passenger for passenger in passengers_in_station
                        if passenger.shape_type in staion_shape_types_in_line
                    ]
                    # 運べる乗客がいなければ発車、いれば先頭の乗客を乗せる
                    if len(passengers_to_pickup) != 0:
                        # 先頭の乗客の現在地を更新
                        passengers_to_pickup[0].update_current_location(train.name)
                    else:
                        # 電車のスタート駅とゴール駅を更新
                        station_name_list = list(self.station_dict.keys())
                        idx = station_name_list.index(train.next_station.name)
                        if idx + 1 < len(station_name_list):
                            name = station_name_list[idx + 1]
                        else:
                            name = station_name_list[0]
                        new_next_station = self.station_dict[name]
                        train.set_stations(train.next_station, new_next_station)
                        train.set_status('move')
            else:
                raise RuntimeError

    def reorder_staions(self, key_list: list):
        if not Counter(key_list) == Counter(self._stations.keys()):
            raise RuntimeError
        new_stations = {}
        # -------------------------------------------
        # TODO: 路線が逆回りになってしまう現象を解決する
        # old_key_list = list(self._stations.keys())
        # for i in range(len(old_key_list)):
        #     if key_list[i] != old_key_list[i]:
        #         print(f'{i+1}-th station is wrong')
        #         print(key_list)
        #         print(old_key_list)
        #         raise RuntimeError
        # -------------------------------------------
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
        train.set_status('stop')

    def remove_station(self, name: str):
        del self._stations[name]
        print(f'remove station {name} from {self._name}')

    def remove_train(self, name: str):
        del self._trains[name]
        print(f'remove train {name} from {self._name}')