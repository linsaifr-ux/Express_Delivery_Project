# -*- coding: utf-8 -*-
from __future__ import annotations
from Order import Order
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Customer import Customer

class Orders_Handler:
    """
    Orders Handler class.
    Manages collection of orders.
    """
    def __init__(self):
        self.__orders: dict[str, Order] = {}
        
    def add(self, order: Order):
        self.__orders[order.ID] = order
        
    def get(self, order_ID: str) -> Order:
        return self.__orders.get(order_ID)
        
    def filter_by_customer(self, customer_ID: str) -> list[Order]:
        pass
        
    def filter_by_date(self, start_date, end_date) -> list[Order]:
        pass
        
    def filter_by_vehicle(self, vehicle) -> list[Order]:
        pass
        
    def filter_by_repo(self, repository) -> list[Order]:
        pass
        
    def filter_delayed(self) -> list[Order]:
        pass
        
    def log(self, order_ID: str, event_type: str, description: list):
        pass
