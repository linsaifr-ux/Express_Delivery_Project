# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Wed Dec 12 15:21:22 2025

@author: Frank
"""
class Package:
    """
    Package class.
    Attributes: size, weight, value, content_description, is_dangerous, is_fragile.
    """
    def __init__(self, size: tuple, weight: float, value: float, content_description: str,
                 is_dangerous: bool, is_fragile: bool):
        self.__size = size
        self.__weight = weight
        self.__value = value
        self.__content_description = content_description
        self.__is_dangerous = is_dangerous
        self.__is_fragile = is_fragile
        
    def add_description(self, description: str):
        self.__content_description += " " + description
    
    @property
    def size(self):
        return self.__size
        
    @property
    def weight(self):
        return self.__weight
        
    @property
    def value(self):
        return self.__value
        
    @property
    def content_description(self):
        return self.__content_description
        
    @property
    def is_dangerous(self):
        return self.__is_dangerous
        
    @property
    def is_fragile(self):
        return self.__is_fragile
