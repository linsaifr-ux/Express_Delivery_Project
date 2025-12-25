# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Thu Dec 25 13:08:25 2025

@author: laisz
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Order import Order

class Location(ABC):
    """
    Attributes:
        address (str): the address of the location
        
    Methods:
        -
    """
    def __init__(self, address: str):
        self._address = address
        
    @property
    def address(self) -> str:
        return self._address
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
class Destination(Location):
    """
    The final destination of a delivery.
    """
    def __str__(self) -> str:
        return self.address
    

class Repository(Location):
    """
    Attributes:
        address (str): the address of the location
        name(str): the name of the repository
        inventory(set[Order]): a list of cargo at the repository
    
    Methods:
        receive(*orders: Order)
        ship(*orders: Order)
    """
    def __init__(self, address: str, name: str):
        super().__init__(address)
        self._name = name
        self._inventory = set()
        
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def inventory(self) -> set[Order]:
        return self._inventory.copy()
    
    
    ## Methods
    def receive(self, *orders: Order) -> None:
        self._inventory |= set(orders)
        
    def ship(self, *orders: Order) -> None:
        self._inventory -= set(orders)
        
    def __str__(self) -> str:
        return self.name