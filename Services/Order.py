# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Fri Dec 26 12:14:49 2025

@author: laisz
"""

from platformdirs import user_data_dir
from enum import Enum
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import json, pickle
from Location import Location, Destination
from Package import Package
from Bill import Bill
from Entry import Entry, Arrival, Transit, OtherEvent
from os.path import join, isfile


def get_dir() -> str:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['order_suffix']

class Order:
    """
    """
    __DATA_PATH = get_dir()
    
    def __init__(self, customer_ID: str,
                 bill_cnt: int, # Customer's bill_cnt
                 service: Service, 
                 origin: Location,
                 destination: Location,
                 receiver_ID: str,
                 is_international: bool,
                 *package_args: tuple):
        self._ID = f"O{customer_ID[1:]}{bill_cnt:05d}"
        self._service = service
        self._collection_day = datetime.now(ZoneInfo("Asia/Taipei"))
        self._due_day = self._collection_date + timedelta(days=service.day)
        self._origin = origin
        self._destination = destination
        self._is_international = is_international
        self._fee = None
        self._bill_ref = None
        self._status = Status.normal
        self._package = Package(*package_args)
        self._log = [Arrival(receiver_ID, origin)]
        
        
    @property
    def ID(self) -> str:
        return self._ID
    
    @property
    def size_class(self) -> SizeClass:
        len_index = sum(self.package.size)
        if len_index <= 60:
            return SizeClass.envelope
        elif len_index <= 90:
            return SizeClass.small_box
        elif len_index <= 120:
            return SizeClass.medium_box
        elif len_index <= 150:
            return SizeClass.big_box
        
    @property
    def weight_class(self) -> WeightClass:
        if self.package.weight <= 0.5:
            return WeightClass.extra_light
        elif self.package.weight <= 5:
            return WeightClass.light
        elif self.package.weight <= 15:
            return WeightClass.heavy
        elif self.package.weight <= 30:
            return WeightClass.extra_heavy
    
    @property
    def service(self) -> str:
        return self._service    
    
    @property
    def collection_date(self) -> date:
        return self._collection_day.date()
    
    @property
    def due_date(self) -> date:
        return self._collection_day.date()
    
    @property
    def origin(self) -> Location:
        return self._origin
    
    @property
    def destination(self) -> Location:
        return self._destination
    
    @property 
    def is_international(self) -> bool:
        return self._is_international
    
    @property
    def fee(self) -> float:
        if self._fee is None:
            self.calc_fee()
        return self._fee
    
    @property
    def bill_ref(self) -> Bill:
        return self._bill_ref
    
    @property
    def status(self) -> Status:
        return self._status
    
    @property
    def package(self) -> Package:
        return self._package
     
    
    ## Methods
    def calc_fee(self) -> float:
        def distance_factor():
            return 1
        total = ((self.service.value * distance_factor(self.origin, self.destination))
                 + max(self.size_class.value, self.weight_class.value)
                 + int(self._package.is_dangerous) * 500
                 + int(self._package.is_fragile) * 100)
        
        return total
    
    def billing(self, bill_ID: str):
        self._bill_ref = bill_ID
        
    
    def new_log(self, _type: str, receiver_ID, *args) -> None:
        _type = _type.upper()
        if _type == 'A':
            if isinstance(args[0], Destination):
                self._status = Status.delivered
            self._log.append(Arrival(receiver_ID, *args))
            return
        elif _type == 'T':
            self._log.append(Transit(receiver_ID, *args))
            return
        elif _type == 'C':
            self._status = Status.broken
        elif _type == 'M':
            self._status = Status.missing
        self._log.append(OtherEvent(receiver_ID, *args))
        return
    
            
    def last_log(self) -> Entry:
        return self._log[-1]
    
    
    def earlier_logs(self, step: int) -> list[Entry]:
        return self._log[-step:]
    
    def all_logs(self) -> list[Entry]:
        return self._log.copy()
    
    def save(self) -> None:
        file_path = join(self.__DATA_PATH, f"{self.ID}.pkl")
        with open(file_path, "wb") as file:
            pickle.dump(self, file, protocol=4)

    @classmethod
    def from_ID(cls, order_ID) -> Order:
        file_path = join(cls.__DATA_PATH, f"{order_ID}.pkl")
        if not isfile(file_path):
            raise FileNotFoundError(f"There's no order with the specifed ID: {order_ID}")
            
        with open(file_path, "rb") as file:
            instance = pickle.load(file)
        
        return instance
    
    
class SizeClass(Enum):
    envelope = 60
    small_box = 120
    medium_box = 250
    big_box = 450
    
class WeightClass(Enum):
    extra_light = 60
    light = 120
    heavy = 250
    extra_heavy = 450
    
class Service(Enum):
    over_night = 2.5
    express = 1.8
    standard = 1.2
    economy = 1.0
    
    @property
    def day(self) -> int:
        """
        Returns
        -------
        int
            The days before the deadline after collection
        """
        if self is Service.over_night:
            return 1
        elif self is Service.express:
            return 2
        elif self is Service.standard:
            return 7
        elif self is Service.economy:
            return 14
        
class Status(Enum):
    normal = 0
    delivered = 1
    delayed = 2
    broken = 3
    missing = 4
    
if __name__ == "__main__":
    print(Service.over_night.value)