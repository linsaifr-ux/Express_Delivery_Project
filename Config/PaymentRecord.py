# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 16:19:21 2025

@author: laisz
"""
from PaymentArrangement import PaymentMethod


class PaymentRecord:        
    def __init__(self, transaction_ID: str, method: PaymentMethod):
        self.__transaction = transaction_ID
        
        if not isinstance(method, PaymentMethod):
            raise TypeError("The method provided is invalid!")
        self.__method = method
        
    @property 
    def transaction(self) -> str:
        return self.__transaction
    
    @property 
    def method(self) -> PaymentMethod:
        return self.__method