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
    """
    Get the data directory path for storing order data.
    
    Returns
    -------
    str
        The full path to the order data directory.
    """
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['order_suffix']

class OrdersHandler:
    """
    Singleton class that manages the collection of orders.

    This class provides centralized access to all orders in the system,
    supporting CRUD operations and various filtering capabilities.

    Methods:
        add(*order_args): Create and add a new order.
        get(order_ID): Retrieve an order by ID.
        filter_by_customer(customer_ID): Get orders for a specific customer.
        filter_by_date(start_date, end_date): Get orders within a date range.
        filter_by_vehicle(vehicle): Get orders on a specific vehicle.
        filter_by_repo(repository): Get orders in a specific repository.
        filter_delayed(): Get all delayed orders.
        log(order_ID, *entry_args): Add a log entry to an order.
    """
    _instance = None
    
    def __new__(cls, *args):
        """
        Create or return the singleton instance of OrdersHandler.

        Returns
        -------
        OrdersHandler
            The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__ORDERS_PATH = get_dir()
            cls._instance._orders = {}
        return cls._instance
        
        
    def add(self, *order_args: tuple) -> str:
        """
        Create a new order and add it to the collection.

        Parameters
        ----------
        *order_args : tuple
            Arguments passed to the Order constructor.

        Returns
        -------
        str
            The ID of the newly created order.
        """
        order = Order(*order_args)
        self._orders[order.ID] = order
        return order.ID
        
    def get(self, order_ID: str) -> Order:
        """
        Retrieve an order by its ID.

        Parameters
        ----------
        order_ID : str
            The ID of the order to retrieve.

        Returns
        -------
        Order
            The requested Order object (from cache or storage).
        """
        return self._orders.get(order_ID, Order.from_ID(order_ID))
        
    def filter_by_customer(self, customer_ID: str) -> list[Order]:
        """
        Get all orders belonging to a specific customer.

        Parameters
        ----------
        customer_ID : str
            The ID of the customer.

        Returns
        -------
        list[Order]
            A list of orders where the payer matches the customer ID.
        """
        targets = []
        for entry in listdir(self.__ORDERS_PATH):
            full_path = join(self.__ORDERS_PATH, entry)
            if not isfile(full_path):
                continue
                
            order = Order.from_ID(entry[:14])
            
            if order.payer == customer_ID:
                targets.append(order)
                
        return targets            
        
        
    def filter_by_date(self, start_date, end_date) -> list[Order]:
        """
        Get all orders with their due date within a date range.

        Parameters
        ----------
        start_date : date
            The start date of the range (inclusive).
        end_date : date
            The end date of the range (inclusive).

        Returns
        -------
        list[Order]
            A list of orders with due dates within the range.
        """
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
        """
        Get all orders currently on a specific vehicle.

        Parameters
        ----------
        vehicle : Vehicle
            The vehicle to query.

        Returns
        -------
        set[Order]
            A set of orders on the vehicle.
        """
        return vehicle.cargo
        
    def filter_by_repo(self, repository: Repository) -> set[Order]:
        """
        Get all orders currently in a specific repository.

        Parameters
        ----------
        repository : Repository
            The repository to query.

        Returns
        -------
        set[Order]
            A set of orders in the repository.
        """
        return repository.inventory
        
    def filter_delayed(self) -> list[Order]:
        """
        Get all orders that are past their due date.

        Returns
        -------
        list[Order]
            A list of delayed orders.
        """
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
        """
        Add a log entry to an order.

        Parameters
        ----------
        order_ID : str
            The ID of the order to update.
        *entry_args
            Arguments passed to Order.new_log().

        Returns
        -------
        None
        """
        self.get(order_ID).new_log(*entry_args)
        
