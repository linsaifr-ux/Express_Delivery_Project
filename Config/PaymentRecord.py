# -*- coding: utf-8 -*-
from __future__ import annotations
from PaymentArrangement import PaymentArrangement
"""
Created on Wed Dec 12 15:21:22 2025

@author: Frank
"""
class Payment_Record:
    """
    Payment Record class.
    Stores transaction ID and payment method.
    """
    def __init__(self, transaction_ID: str, payment_method: PaymentArrangement):
        """
        Initialize Payment Record.
        
        Parameters
        ----------
        transaction_ID : str
            The transaction ID.
        payment_method : PaymentArrangement
            The method of payment.
        """
        self.__transaction_ID = transaction_ID
        self.__payment_method = payment_method
        
    @property
    def transaction_ID(self) -> str:
        return self.__transaction_ID
        
    @property
    def payment_method(self) -> PaymentArrangement:
        return self.__payment_method
