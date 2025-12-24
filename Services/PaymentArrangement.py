# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 21:45:31 2025

@author: laisz
"""
from enum import Enum
    

class PaymentMethod(Enum):
    """
    A class that define how the bill will be payed.
    
    cash    : payed by cash
    card    : payed by credit card
    wire    : payment wired
    """
    cash = 0
    card = 1
    wire = 2
    
class BillingTiming(Enum):
    """
    A class that define when the bill will be issued.
    
    in_advance : when the order is first created
    on_delivery: when the order is delivered
    monthly    : at the end of a month, covering all orders created in that
                 month
    """
    in_advance = 0
    on_delivery = 1
    monthly = 2