# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Fri Dec 26 11:22:49 2025

@author: laisz
"""
from platformdirs import user_data_dir
from Order import Order
from Vehicle import Vehicle
from Location import Repository
import json
from os.path import isfile, join


def get_dir() -> str:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['order_suffix']

class Orders_Handler:
    """
    Orders Handler class.
    Manages collection of orders.
    """
    _ORDERS_PATH = get_dir()
    
    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = cls(*args)
            
        return cls._instance
            
    def __init__(self):
        self._orders = {}
        
    def add(self, *order_args: tuple) -> str:
        order = Order(*order_args)
        self._orders[order.ID] = order
        return order.ID
        
    def get(self, order_ID: str) -> Order:
        return self._orders.get(order_ID, Order.from_ID(order_ID))
        
    def filter_by_customer(self, customer_ID: str, bill_cnt: int) -> list[Order]:
        orders = []
        for i in range(bill_cnt):
            file_path = join(self._ORDERS_PATH, f"{customer_ID[1:]}{i:05d}")
            
            if not isfile(file_path):
                continue
            orders.append(Order.from_ID(file_path))
            
        return orders            
        
        
    def filter_by_date(self, start_date, end_date) -> list[Order]:
        pass
        
    def filter_by_vehicle(self, vehicle: Vehicle) -> set[Order]:
        return vehicle.cargo
        
    def filter_by_repo(self, repository: Repository) -> set[Order]:
        return repository.inventory
        
    def filter_delayed(self) -> list[Order]:
        pass
        
    def log(self, order_ID: str, event_type: str, description: list):
        pass
