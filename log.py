# log.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

class Logger:
    def __init__(self, world, path='./outputs/run_0'):
        self._world = world
        self._path = path

    def save(self):
        # get record data
        station_info = {}
        for station in self._world.station_dict.values():
            station_info[station.name] = {
                'x': station.x,
                'y': station.y,
                'shape_type': station.shape_type,
            }
        
        train_info = {}
        for train in self._world.train_dict.values():
            train_info[train.name] = {
                'x': train.x,
                'y': train.y,
            }

        passenger_info = {}
        for passenger in self._world.passenger_dict.values():
            passenger_info[passenger.name] = {
                'shape_tpye': passenger.shape_type,
                'current_location': passenger.current_location,
            }
        
        line_info = {}
        for line in self._world.line_dict.values():
            line_info[line.name] = {
                'route': list(line.station_dict.keys())
            }

        record = {
            'clock': self._world.clock,
            'stations': station_info,
            'trains': train_info,
            'passengers': passenger_info,
            'lines': line_info,

        }
        # write into json file
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
