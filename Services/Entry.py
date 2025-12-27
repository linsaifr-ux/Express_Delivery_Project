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
    An abstract base class representing an entry in a cargo's history log.

    Attributes:
        signature: Identifier of the person/system creating the entry.
        time_stamp (datetime): The timestamp when the entry was created (Asia/Taipei timezone).

    Methods:
        summarize(): Returns a string summary of the entry.
    """
    def __init__(self, signature):
        """
        Initialize an Entry.

        Parameters
        ----------
        signature
            Identifier of the person or system creating this entry.
        """
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
        """
        Generate a string summary of the entry.

        Returns
        -------
        str
            A human-readable summary of the entry.
        """
        pass
    

class Transit(Entry):
    """
    Represents a transit event where a package is shipped between locations.

    Attributes:
        vehicle (Vehicle): The vehicle used for transportation.
        origin (Location): The starting location of the transit.
        destination (Location): The destination location of the transit.

    Methods:
        summarize(): Returns a string summary of the transit event.
    """
    def __init__(self, signature,
                 vehicle: Vehicle, origin: Location, destination: Location):
        """
        Initialize a Transit entry.

        Parameters
        ----------
        signature
            Identifier of the person or system creating this entry.
        vehicle : Vehicle
            The vehicle used for transportation.
        origin : Location
            The starting location of the transit.
        destination : Location
            The destination location of the transit.
        """
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
        """
        Generate a string summary of the transit event.

        Returns
        -------
        str
            A human-readable summary of the transit.
        """
        return self.__str__()
        

class Arrival(Entry):
    """
    Represents an arrival event where a package arrives at a location.

    Attributes:
        destination (Location): The location where the package arrived.

    Methods:
        summarize(): Returns a string summary of the arrival event.
    """
    def __init__(self, signature, destination: Location):
        """
        Initialize an Arrival entry.

        Parameters
        ----------
        signature
            Identifier of the person or system creating this entry.
        destination : Location
            The location where the package arrived.
        """
        super().__init__(signature)
        self._destination = destination
        
    @property
    def destination(self) -> Location:
        return self._destination
    
    def __str__(self) -> str:
        return (self.time_stamp.__str__()
                + " The package arrived at " + self.destination.__str__() + ".")
    
    def summarize(self) -> str:
        """
        Generate a string summary of the arrival event.

        Returns
        -------
        str
            A human-readable summary of the arrival.
        """
        return self.__str__()
    

class OtherEvent(Entry):
    """
    Represents a miscellaneous event in the package's history.

    Attributes:
        summary (str): A brief summary of the event.
        detail (str): A detailed description of the event.

    Methods:
        summarize(): Returns a string summary including the detail.
    """
    def __init__(self, signature, summary: str, description: str = None):
        """
        Initialize an OtherEvent entry.

        Parameters
        ----------
        signature
            Identifier of the person or system creating this entry.
        summary : str
            A brief summary of the event.
        description : str, optional
            A detailed description of the event. Defaults to summary if not provided.
        """
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
        """
        Generate a string summary of the event.

        Returns
        -------
        str
            A summary string combining summary and detail.
        """
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
    
    