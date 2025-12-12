# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 11:33:23 2025

@author: laisz
"""
from enum import Enum

class BillingPref(Enum):
    in_advance = 0
    on_delivery = 1
    monthly = 2
    