# -*- coding: utf-8 -*-
"""
Created on Sat Dec 27 16:00:03 2025

@author: green
"""
from OrdersHandler import OrdersHandler
from Staff import Staff

class CSStaff(Staff):

    def __init__(self, first_name: str, last_name: str, position: str, password: str):
        super().__init__(first_name, last_name, position, password)
        self._handler = OrdersHandler()
    '''
    All data is inherited from Staff, 
    and calls methods from OrdersHandler.
    
    filter_by_customer(Customer.ID)
    filter_by_date(start_date, end_date)
    filter_by_vehicle(vehicle)
    filter_delayed()
    '''
    def filter_by_customer(self, customer_ID: str):
        
        return self._handler.filter_by_customer(customer_ID)

    def filter_by_date(self, start_date, end_date):
        
        return self._handler.filter_by_date(start_date, end_date)
    
    def filter_delayed(self):
        
        return self._handler.filter_delayed()