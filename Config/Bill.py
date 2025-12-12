# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Wed Dec 10 21:26:22 2025

@author: laisz
"""
<<<<<<< HEAD
from PaymentRecord import PaymentRecord
from PaymentArrangement import PaymentMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Customer import Customer
    

def verify_transaction(transaction_ID, amount) -> bool:
    "A mock up for verifying a transaction."
    return True

class Bill:        
    # NameError resolved
    def __init__(self, outer_ref: Customer, ID: int, payment_amount: float,
                  order_ID: str):
        self.outer = outer_ref
        self.__ID = "B" + str(self.outer.ID)[1:] + f"{self.outer.bill_cnt: 04d}"
        self.__amount = payment_amount
        self.__payment_status = False
        self.__payment_record = None
        self.__manifest = [order_ID]
    
    @property
    def ID(self) -> str:
        return self.__ID
    
    @property
    def amount(self) -> float:
        return self.__amount
        
    @property
    def payment_status(self) -> bool:
        return self.__payment_status
    
    @property
    def payment_record(self) -> PaymentRecord:
        return self.__payment_record
    
    @property
    def manifest(self) -> list[str]:
        return self.__manifest.copy()

    
    ## Methods
    def pay(self, transaction_ID: str, method: PaymentMethod) -> None:        
        if verify_transaction(transaction_ID, self.amount):
            self.__payment_status = True
            self.__payment_record = PaymentRecord(transaction_ID, method)
        else:
            print("Error, The transaction ID provided is invalid!")
            
    def verify_payment(self) -> bool:
        """
        Verify if the bill has been paid.
        """
        return self.__payment_status
    
    def add_item(self, order: Order) -> None:
        self.__manifest.append(order.ID)
        self.__amount += order.fee