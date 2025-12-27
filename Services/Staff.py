# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Sat Dec 27 10:45:00 2025

@author: Frank
"""
from platformdirs import user_data_dir
import json, pickle
import os
from os import listdir, remove
from os.path import isfile, join
from OrderHandler import OrdersHandler
from Order import Order
from Vehicle import Vehicle, Minivan, MiniTruck, Truck
from Location import Location, Repository, Destination
from Entry import Entry, Arrival, Transit, OtherEvent
from datetime import date

def get_dir() -> str:
    """
    Get the data directory path for storing staff data.
    
    Returns
    -------
    str
        The full path to the staff data directory.
    """
    with open(join(os.path.dirname(__file__), 'config.json'), 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return user_data_dir(config['app_name'], config['project_name']) + config['staff_suffix']

class Staff:
    """
    Represents a staff member in the package delivery system.

    Attributes:
        ID (str): The unique identifier for the staff.
        first_name (str): The staff's first name.
        last_name (str): The staff's last name.
        position (str): The staff's position/role.
        password (str): The staff's password for authentication.

    Methods:
        verify(password): Verify if the provided password matches.
        save(): Save the staff data to local storage.
        from_ID(ID): Class method to load a staff from stored data.
        get(order_ID): Get an order by its ID.
    """
    ## Class attribute
    __DATA_PATH = get_dir()
    try:
        _cnt = len([f for f in listdir(__DATA_PATH) if f.endswith('.pkl')])
    except FileNotFoundError:
        _cnt = 0
    
    def __init__(self, first_name: str, last_name: str, position: str, password: str):
        """
        Initialize a new Staff member.

        Parameters
        ----------
        first_name : str
            The staff's first name.
        last_name : str
            The staff's last name.
        position : str
            The staff's position (e.g., 'Driver', 'Manager').
        password : str
            The staff's password.
        """
        self._ID = f"S{self._cnt:05d}"
        self._first_name = first_name
        self._last_name = last_name
        self._position = position
        self._password = password
        
        # Check if ID already exists (unlikely with auto-increment but good for safety)
        if isfile(join(self.__DATA_PATH, f"{self.ID}.pkl")):
             # If collision (e.g. deleted files), verify next available
             while isfile(join(self.__DATA_PATH, f"S{self._cnt:05d}.pkl")):
                 self.__class__._cnt += 1
             self._ID = f"S{self._cnt:05d}"

        self.__class__._cnt += 1
        
    @property
    def ID(self) -> str:
        return self._ID

    @property
    def first_name(self) -> str:
        return self._first_name
    
    @property
    def last_name(self) -> str:
        return self._last_name
    
    @property
    def position(self) -> str:
        return self._position
    
    @property
    def password(self) -> str:
        return self._password

    def verify(self, password: str) -> bool:
        """
        Verify if the provided password matches the staff's password.

        Parameters
        ----------
        password : str
            The password to verify.

        Returns
        -------
        bool
            True if the password matches, False otherwise.
        """
        return self._password == password
        
    def get(self, order_ID: str) -> Order:
        """
        Get an order by its ID.
        """
        return OrdersHandler().get(order_ID)
        
    def save(self) -> None:
        """
        Save the Staff object's field as a pkl file in local directory.
        """
        # Ensure directory exists
        import os
        if not os.path.exists(self.__DATA_PATH):
            os.makedirs(self.__DATA_PATH)
            
        with open(join(self.__DATA_PATH, f"{self.ID}.pkl"), 'wb') as file:
            pickle.dump(self, file, protocol=4)
        return
    
    def __str__(self) -> str:
        return (f"Name\t: {self.first_name} {self.last_name}\n"
                + f"ID\t\t: {self.ID}\n"
                + f"Position\t: {self.position}")

    @classmethod
    def from_ID(cls, ID: str) -> Staff:
        """
        Factory method to reconstruct the staff instance base on <ID>.pkl.
        
        Parameters
        ----------
        ID : str
            The ID of the staff instance to reconstruct.

        Returns
        -------
        Staff
            The loaded Staff instance.
        """
        file_path = join(cls.__DATA_PATH , f"{ID}.pkl")
        if not isfile(file_path):
            raise FileNotFoundError("The Staff with the provided ID does not exist!")
            
        with open(file_path, 'rb') as file:
            instance = pickle.load(file)
        
        return instance
    
    @classmethod
    def delete(cls, ID: str) -> None:
        """
        Delete the staff file from storage.
        
        Parameters
        ----------
        ID : str
            The ID of the staff to delete.
        """
        file_path = join(cls.__DATA_PATH , f"{ID}.pkl")
        if isfile(file_path):
            remove(file_path)

class RepoStaff(Staff):
    def __init__(self, first_name: str, last_name: str, position: str, password: str, repository: Repository):
        super().__init__(first_name, last_name, position, password)
        self._repository = repository

    def package_at_repo(self) -> set[Order]:
        return OrdersHandler().filter_by_repo(self._repository)

    def report_arrival(self, order_ID: str):
        OrdersHandler().log(order_ID, 'A', self.ID, self._repository)
        self._repository.receive(OrdersHandler().get(order_ID))

    def report_damage(self, order_ID: str, description: str):
        OrdersHandler().log(order_ID, 'C', self.ID, "Damage Reported", description)

    def report_lost(self, order_ID: str, description: str):
         OrdersHandler().log(order_ID, 'M', self.ID, "Loss Reported", description)

class Driver(Staff):
    def __init__(self, first_name: str, last_name: str, position: str, password: str, vehicle: Vehicle):
        super().__init__(first_name, last_name, position, password)
        self._vehicle = vehicle

    def package_on_vehicle(self) -> set[Order]:
        return OrdersHandler().filter_by_vehicle(self._vehicle)

    def report_transit(self, order_ID: str):
        order = OrdersHandler().get(order_ID)
        OrdersHandler().log(order_ID, 'T', self.ID, self._vehicle, order.origin, order.destination)
        self._vehicle.pick_up(order)

    def report_delivered(self, order_ID: str):
        order = OrdersHandler().get(order_ID)
        OrdersHandler().log(order_ID, 'A', self.ID, order.destination)
        self._vehicle.deliver(order)

    def report_damage(self, order_ID: str, description: str):
        OrdersHandler().log(order_ID, 'C', self.ID, "Damage Reported", description)

    def report_lost(self, order_ID: str, description: str):
        OrdersHandler().log(order_ID, 'M', self.ID, "Loss Reported", description)

class CSStaff(Staff):
    def filter_by_customer(self, customer_ID: str) -> list[Order]:
        return OrdersHandler().filter_by_customer(customer_ID)

    def filter_by_date(self, start_date: date, end_date: date) -> list[Order]:
        return OrdersHandler().filter_by_date(start_date, end_date)

    def filter_delayed(self) -> list[Order]:
        return OrdersHandler().filter_delayed()

class Management(Staff):
    def filter_by_customer(self, customer_ID: str) -> list[Order]:
        return OrdersHandler().filter_by_customer(customer_ID)

    def filter_by_date(self, start_date: date, end_date: date) -> list[Order]:
        return OrdersHandler().filter_by_date(start_date, end_date)
    
    def filter_by_vehicle(self, vehicle: Vehicle) -> set[Order]:
        return OrdersHandler().filter_by_vehicle(vehicle)
        
    def filter_by_repo(self, repository: Repository) -> set[Order]:
        return OrdersHandler().filter_by_repo(repository)

    def filter_delayed(self) -> list[Order]:
        return OrdersHandler().filter_delayed()

    def add_vehicle(self, type: str, license_plate: str) -> Vehicle:
        type_lower = type.lower()
        if "truck" in type_lower and "mini" in type_lower:
             return MiniTruck(license_plate)
        elif "truck" in type_lower:
             return Truck(license_plate)
        elif "minivan" in type_lower:
             return Minivan(license_plate)
        else:
             return Minivan(license_plate)

    def add_repo(self, address: str, name: str) -> Repository:
        return Repository(address, name)

if __name__ == "__main__":
    def check_pickleability(obj):
        try:
            pickle.dumps(obj)
            print("Everything in the composition is pickleable!")
        except Exception as e:
            print(f"Pickle Error found: {e}")

    # Test Run
    print("--- Creating Staff ---")
    s = Staff("John", "Doe", "Driver", "securepass")
    print(s)
    
    print("\n--- Checking Pickleability ---")
    check_pickleability(s)
    
    print("\n--- Saving Staff ---")
    s.save()
    print("Saved.")
    
    print("\n--- Loading Staff from ID ---")
    loaded_s = Staff.from_ID(s.ID)
    print(f"Loaded: {loaded_s}")
    
    print("\n--- Verifying Password ---")
    print(f"Verify 'securepass': {loaded_s.verify('securepass')}")
    print(f"Verify 'wrongpass': {loaded_s.verify('wrongpass')}")