# -*- coding: utf-8 -*-
"""
Created on Thu Dec 25 14:04:34 2025

@author: laisz
"""
from abc import ABC, abstractmethod
from datetime import datetime
from zoneinfo import ZoneInfo
from Location import Location
from Vehicle import Vehicle


class Entry(ABC):
    """
    An entry to cargo's history log.
    
    Attributes:
        
    Methods:
        
    """
    def __init__(self, signature):
        self._signature = signature
        self._time_stamp = datetime.now(ZoneInfo("Asia/Taipei"))
        
    @property
    def signature(self):
        return self._signature
    
    @property
    def time_stamp(self) -> datetime:
        return self._time_stamp
    
    @abstractmethod
    def summarize() -> str:
        pass
    

class Transit(Entry):
    """
    """
    def __init__(self, signature,
                 vehicle: Vehicle, origin: Location, destination: Location):
        super().__init__(signature)
        self._vehicle = vehicle
        self._origin = origin
        self._destination = destination
        
    @property
    def vehicle(self) -> Vehicle:
        return self._vehicle
    
    @property
    def origin(self) -> Location:
        return self._origin
    
    @property
    def destination(self) -> Location:
        return self._destination
    
    def __str__(self) -> str:
        return (self.time_stamp.__str__()
                + " The package was shipped out of " + self.origin.__str__()
                + " on " + self.vehicle.__str__()
                + ", bound for " + self.destination.__str__() + ".")
    
    def summarize(self) -> str:
        return self.__str__()
        

class Arrival(Entry):
    """
    """
    def __init__(self, signature, destination: Location):
        super().__init__(signature)
        self._destination = destination
        
    @property
    def destination(self) -> Location:
        return self._destination
    
    def __str__(self) -> str:
        return (self.time_stamp.__str__()
                + " The package arrived at " + self.destination.__str__() + ".")
    
    def summarize(self) -> str:
        return self.__str__()
    

class OtherEvent(Entry):
    """
    """
    def __init__(self, signature, summary: str, description: str = None):
        super().__init__(signature)
        self._summary = summary
        if description is None:
            self._detail = summary
        else:
            self._detail = description
            
    @property
    def summary(self) -> str:
        return self._summary
    
    @property
    def detail(self) -> str:
        return self._detail
    
    def summarize(self) -> str:
        return self.summary + ". " + self.detail
    
    def __str__(self) -> str:
        return (self.time_stamp.__str__() + " "
                + self.summarize())
    

if __name__ == "__main__":
    from Vehicle import Minivan
    from Location import Repository
    
    carA = Minivan("AAA-0000")
    Repo0 = Repository("Brooklyn", "Repo0")
    Repo1 = Repository("New York", "Repo1")
    
    print(Transit(2143, carA, Repo0, Repo1))
    print(Arrival(2143, Repo1))
    print(OtherEvent(2143, "Accident", "The package fall on the ground and break."))
    
    