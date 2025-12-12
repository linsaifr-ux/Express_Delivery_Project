# -*- coding: utf-8 -*-

from __future__ import annotations
"""
Created on Wed Dec 12 15:21:22 2025

@author: Frank
"""
from PaymentArrangement import PaymentMethod


class PaymentRecord:
    """
    Payment Record class.
    Stores transaction ID and payment method.
    """
    def __init__(self, transaction_ID: str, method: PaymentMethod):
        """
        Initialize Payment Record.
        
        Parameters
        ----------
        transaction_ID : str
            The transaction ID.
        method : PaymentMethod
            The method of payment.
        """
        self.__transaction_ID = transaction_ID
        
        if not isinstance(method, PaymentMethod):
            raise TypeError("The method provided is invalid!")
        self.__method = method
        
    @property
    def transaction_ID(self) -> str:
        return self.__transaction_ID
        
    @property
    def method(self) -> PaymentMethod:
        return self.__method