# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Wed Dec 10 21:26:22 2025

@author: laisz
"""
from PaymentArrangement import PaymentArrangement

class Bill:
    # NameError resolved
    def __init__(self, outer_ref: Customer, ID: int, payment_amount: float,
                  order_ID: str):
        self.outer = outer_ref
        self.__ID = "B" + str(self.outer.ID)[1:] + str(self.outer.bill_cnt)
        self.__amount = payment_amount
        self.payment_arrangement = None
        self.__payment_status = False
        self.__manifest = []
    
    @property
    def ID(self) -> str:
        return self.__ID
    
    @property
    def amount(self) -> float:
        return self.__amount
        
    @property
    def payment_arrangement(self) -> PaymentArrangement:
        return self.__payment_arrangement
    
    @payment_arrangement.setter
    def payment_arrangement(self, arrangement: PaymentArrangement):
        if not isinstance(arrangement, PaymentArrangement):
            raise ValueError("Invalid payment arrangement!")
        self.__payment_arrangement = arrangement
        
    @property
    def payment_status(self) -> bool:
        return self.__payment_status
    
    
    
        
    