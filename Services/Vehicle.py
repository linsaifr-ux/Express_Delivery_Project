# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Thu Dec 25 12:44:55 2025

@author: laisz
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Order import Order

class Vehicle(ABC):
    """
    Attributes:
        license_plate (str): The license plate number of the vehicle
        cargo (set[Order]): A list of cargo that is on the vehicle
        
    Methods:
        pick_up(*order): put the cargos onto the vehicle
        deliver(order): take the cargo off the vehicle, and return what is 
                        removed as a set
    """
    def __init__(self, plate: str):
        self._license_plate = plate
        self._cargo = set()
        
    @property
    def license_plate(self) -> str:
        return self._license_plate
    
    @property
    def cargo(self) -> set[Order]:
        return self._cargo.copy()
    
    ## Methods
    def pick_up(self, *orders: Order) -> None:
        self._cargo |= set(orders)
        
    def deliver(self, order: Order) -> Order:
        self._cargo.remove(order)
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    
class Minivan(Vehicle):
    def __str__(self) -> str:
        return f"minivan ({self.license_plate})"

class MiniTruck(Vehicle):
    def __str__(self) -> str:
        return f"mini truck ({self.license_plate})"

class Truck(Vehicle):
    def __str__(self) -> str:
        return f"truck ({self.license_plate})"

if __name__ == "__main__":
    car = Truck("ABC-1234")
    print(car)
    
        