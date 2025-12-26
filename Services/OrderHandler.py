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
import json, pickle
from os import listdir
from os.path import isfile, join
from datetime import datetime
from zoneinfo import ZoneInfo


def get_dir() -> str:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['order_suffix']

class OrdersHandler:
    """
    Orders Handler class.
    Manages collection of orders.
    """
    __ORDERS_PATH = get_dir()
    
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
        targets = []
        for entry in listdir(self.__ORDERS_PATH):
            full_path = join(self.__ORDERS_PATH, entry)
            if not isfile(full_path):
                continue
                
            with open(full_path, "rb") as file:
                order = pickle.load(file)
            
            if order.due_date >= start_date and order.due_date <= end_date:
                targets.append(order)
                
        return targets
                
                
        
    def filter_by_vehicle(self, vehicle: Vehicle) -> set[Order]:
        return vehicle.cargo
        
    def filter_by_repo(self, repository: Repository) -> set[Order]:
        return repository.inventory
        
    def filter_delayed(self) -> list[Order]:
        targets = []
        for entry in listdir(self.__ORDERS_PATH):
            full_path = join(self.__ORDERS_PATH, entry)
            if not isfile(full_path):
                continue
                
            with open(full_path, "rb") as file:
                order = pickle.load(file)
                
            if order.due_date <= datetime.now(ZoneInfo("Asia/Taipei")).date():
                targets.append(order)
                
        
    def log(self, order_ID: str, *entry_args):
        self.get(order_ID).new_log(*entry_args)
        
