# -*- coding: utf-8 -*-
"""
Created on Sat Dec 27 17:12:20 2025

@author: green
"""
from Location import Destination
from PaymentArrangement import BillingTiming
from Customer import Customer

class Normal(Customer):
    def __init__(self, first_name: str, last_name: str, address:Destination,
                 phone_number: str, email: str,password: str, 
                 billing_pref: BillingTiming,card:str):
        super.__init__(first_name, last_name, address,phone_number,email,password,billing_pref)
        self._card=card
        
    @property
    def card(self) ->str:
        return self._card
    
class Contracted(Customer):
    def __init__(self,first_name: str, last_name: str, address:Destination,
                 phone_number: str, email: str,password: str, 
                 billing_pref: BillingTiming,account:str):
        super.__init__(first_name, last_name, address,phone_number,email,password,billing_pref)
        self._account=account
        
    @property
    def account(self) ->str:
        return self._account
        
class Sponsored(Customer):
    pass


