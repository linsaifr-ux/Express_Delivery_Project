# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Created on Fri Dec 26 12:14:49 2025

@author: laisz
"""

from platformdirs import user_data_dir
from enum import Enum
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import json, pickle
from Location import Location, Destination
from Package import Package
from Bill import Bill
from Entry import Entry, Arrival, Transit, OtherEvent
from PaymentArrangement import BillingTiming
from os import listdir
from os.path import join, isfile



def get_dir() -> str:
    """
    Get the data directory path for storing order data.
    
    Returns
    -------
    str
        The full path to the order data directory.
    """
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
        
    return join(user_data_dir(config['app_name'], config['project_name']), config['order_suffix'])

class Order:
    """
    Represents a delivery order in the package delivery system.

    Attributes:
        payer (str): The customer ID who pays for the order.
        ID (str): The unique identifier for the order.
        size_class (SizeClass): Size classification based on package dimensions.
        weight_class (WeightClass): Weight classification based on package weight.
        service (Service): The service type selected for delivery.
        collection_date (date): The date when the package was collected.
        due_date (date): The expected delivery date.
        origin (Location): The origin location of the package.
        destination (Location): The destination location of the package.
        is_international (bool): Whether this is an international shipment.
        fee (float): The calculated fee for the order.
        bill_ref (Bill): Reference to the associated bill.
        bill_timing (BillingTiming): When the bill should be issued.
        status (Status): The current status of the order.
        package (Package): The package being delivered.

    Methods:
        calc_fee(): Calculate the delivery fee.
        billing(bill_ID): Associate a bill with the order.
        new_log(_type, receiver_ID, *args): Add a new log entry.
        last_log(): Get the most recent log entry.
        earlier_logs(step): Get recent log entries.
        all_logs(): Get all log entries.
        save(): Save the order to local storage.
        from_ID(order_ID): Load an order from storage.
    """
    __DATA_PATH = get_dir()
    __order_cnt = len(listdir(__DATA_PATH))
    
    def __init__(self, customer_ID: str,
                 bill_timing: BillingTiming,
                 service: Service, 
                 origin: Location,
                 destination: Location,
                 collector_ID: str,
                 is_international: bool,
                 *package_args: tuple):
        """
        Initialize a new Order.

        Parameters
        ----------
        customer_ID : str
            The ID of the customer paying for the order.
        bill_timing : BillingTiming
            When the bill should be issued.
        service : Service
            The delivery service type.
        origin : Location
            The origin location of the package.
        destination : Location
            The destination location of the package.
        collector_ID : str
            The ID of the staff collecting the package.
        is_international : bool
            Whether this is an international shipment.
        *package_args : tuple
            Arguments passed to create the Package.
        """
        self._payer = customer_ID
        self._ID = f"O{self.__order_cnt:013d}"
        self._service = service
        self._collection_day = datetime.now(ZoneInfo("Asia/Taipei"))
        self._due_day = self._collection_day + timedelta(days=service.day)
        self._origin = origin
        self._destination = destination
        self._is_international = is_international
        self._fee = None
        self._bill_ref = None
        self._bill_timing = bill_timing
        self._status = Status.normal
        self._package = Package(*package_args)
        self._log = [Arrival(collector_ID, origin)]
        Order.__order_cnt += 1
        
    @property
    def payer(self) -> str:
        return self._payer
    
    @property
    def ID(self) -> str:
        return self._ID
    
    @property
    def size_class(self) -> SizeClass:
        len_index = sum(self.package.size)
        if len_index <= 60:
            return SizeClass.envelope
        elif len_index <= 90:
            return SizeClass.small_box
        elif len_index <= 120:
            return SizeClass.medium_box
        elif len_index <= 150:
            return SizeClass.big_box
        
    @property
    def weight_class(self) -> WeightClass:
        if self.package.weight <= 0.5:
            return WeightClass.extra_light
        elif self.package.weight <= 5:
            return WeightClass.light
        elif self.package.weight <= 15:
            return WeightClass.heavy
        elif self.package.weight <= 30:
            return WeightClass.extra_heavy
    
    @property
    def service(self) -> str:
        return self._service    
    
    @property
    def collection_date(self) -> date:
        return self._collection_day.date()
    
    @property
    def due_date(self) -> date:
        return self._due_day.date()
    
    @property
    def origin(self) -> Location:
        return self._origin
    
    @property
    def destination(self) -> Location:
        return self._destination
    
    @property 
    def is_international(self) -> bool:
        return self._is_international
    
    @property
    def fee(self) -> float:
        if self._fee is None:
            self._fee = self.calc_fee()
        return self._fee
    
    @property
    def bill_ref(self) -> Bill:
        return self._bill_ref
    
    @property
    def bill_timing(self) -> BillingTiming:
        return self._bill_timing
    
    @bill_timing.setter
    def bill_timing(self, timing: BillingTiming) -> None:
        if not isinstance(timing, BillingTiming):
            raise TypeError("{timing} is not of type BillingTiming")
        
        self._bill_timing = timing
    
    @property
    def status(self) -> Status:
        return self._status
    
    @property
    def package(self) -> Package:
        return self._package
     
    
    ## Methods
    def calc_fee(self) -> float:
        """
        Calculate the delivery fee based on service, distance, size, weight, and special handling.

        Fee Formula
        -----------
        total = (service_multiplier × distance_factor)
                + max(size_class_fee, weight_class_fee)
                + dangerous_goods_surcharge (500 if applicable)
                + fragile_surcharge (100 if applicable)

        Distance Factor
        ---------------
        The distance factor is calculated based on Taiwan county/city names
        (first 3 characters of address):
        
        - 1.0 : Same county (e.g., 高雄市 → 高雄市)
        - 1.2 : Same region (e.g., 高雄市 → 台南市)
        - 2.0 : Different regions (e.g., 北部 → 南部)
        - 2.5 : Offshore islands (澎湖縣, 金門縣, 連江縣)
        - 3.0 : International / Non-Taiwan addresses

        Returns
        -------
        float
            The calculated fee for the order.

        See Also
        --------
        Service : Enum defining service types and their fee multipliers.
        SizeClass : Enum defining size classifications and fee values.
        WeightClass : Enum defining weight classifications and fee values.
        """
        def distance_factor(origin: Location, destination: Location) -> float:
            """
            Calculate distance factor based on county names (first 3 characters of address).
            
            Taiwan is divided into 5 regions:
            - Region 0: 北部 (Taipei, New Taipei, Keelung, Taoyuan, Hsinchu, Yilan)
            - Region 1: 中部 (Miaoli, Taichung, Changhua, Nantou, Yunlin)
            - Region 2: 南部 (Chiayi, Tainan, Kaohsiung, Pingtung)
            - Region 3: 東部 (Hualien, Taitung)
            - Region 4: 離島 (Penghu, Kinmen, Matsu)
            
            Returns
            -------
            float
                Distance multiplier:
                - 1.0 : Same county
                - 2.5 : Offshore islands
                - 1.2 : Same region, different county
                - 2.0 : Different regions
                - 3.0 : International / Non-Taiwan (address not recognized)
            """
            # Region mapping: County prefix (first 3 chars) -> region code
            # Region 0: Northern Taiwan (北部)
            # Region 1: Central Taiwan (中部)
            # Region 2: Southern Taiwan (南部)
            # Region 3: Eastern Taiwan (東部)
            # Region 4: Offshore Islands (離島)
            COUNTY_TO_REGION = {
                # Northern Taiwan (北部) - Region 0
                "台北市": 0, "臺北市": 0,
                "新北市": 0,
                "基隆市": 0,
                "桃園市": 0,
                "新竹市": 0, "新竹縣": 0,
                "宜蘭縣": 0,
                # Central Taiwan (中部) - Region 1
                "苗栗縣": 1,
                "台中市": 1, "臺中市": 1,
                "彰化縣": 1,
                "南投縣": 1,
                "雲林縣": 1,
                # Southern Taiwan (南部) - Region 2
                "嘉義市": 2, "嘉義縣": 2,
                "台南市": 2, "臺南市": 2,
                "高雄市": 2,
                "屏東縣": 2,
                # Eastern Taiwan (東部) - Region 3
                "花蓮縣": 3,
                "台東縣": 3, "臺東縣": 3,
                # Offshore Islands (離島) - Region 4
                "澎湖縣": 4,
                "金門縣": 4,
                "連江縣": 4,
            }
            
            # Extract first 3 characters from address
            origin_county = str(origin.address)[:3]
            dest_county = str(destination.address)[:3]
            
            # Get region codes (default to region 5 if not found)
            origin_region = COUNTY_TO_REGION.get(origin_county, 5)
            dest_region = COUNTY_TO_REGION.get(dest_county, 5)
            
            # Not in Taiwan
            if origin_region == 5 or dest_region == 5:
                return 3.0
            
            # Same county
            if origin_county == dest_county:
                return 1.0

            # Offshore islands always have higher factor
            if origin_region == 4 or dest_region == 4:
                return 2.5
            
            # Same region
            if origin_region == dest_region:
                return 1.2          
            
            # Different regions
            return 2.0
            
        total = ((self.service.value * distance_factor(self.origin, self.destination))
                 + max(self.size_class.value, self.weight_class.value)
                 + int(self._package.is_dangerous) * 500
                 + int(self._package.is_fragile) * 100)
        
        return total
    
    def billing(self, bill_ID: str):
        """
        Associate a bill with this order.

        Parameters
        ----------
        bill_ID : str
            The ID of the bill to associate with this order.
        """
        self._bill_ref = bill_ID
        
    
    def new_log(self, _type: str, receiver_ID, *args) -> None:
        """
        Add a new log entry to the order's history.

        Parameters
        ----------
        _type : str
            Entry type: 'A' for Arrival, 'T' for Transit, 'C' for broken,
            'M' for missing, or other for generic event.
        receiver_ID
            The ID of the person/system creating the log entry.
        *args
            Additional arguments passed to the Entry constructor.

        Returns
        -------
        None
        """
        _type = _type.upper()
        if _type == 'A':
            if isinstance(args[0], Destination):
                self._status = Status.delivered
            self._log.append(Arrival(receiver_ID, *args))
            return
        elif _type == 'T':
            self._log.append(Transit(receiver_ID, *args))
            return
        elif _type == 'C':
            self._status = Status.broken
        elif _type == 'M':
            self._status = Status.missing
        self._log.append(OtherEvent(receiver_ID, *args))
        return
    
            
    def last_log(self) -> Entry:
        """
        Get the most recent log entry.

        Returns
        -------
        Entry
            The most recent log entry.
        """
        return self._log[-1]
    
    
    def earlier_logs(self, step: int) -> list[Entry]:
        """
        Get the most recent log entries.

        Parameters
        ----------
        step : int
            Number of recent entries to retrieve.

        Returns
        -------
        list[Entry]
            A list of recent log entries.
        """
        return self._log[-step:]
    
    def all_logs(self) -> list[Entry]:
        """
        Get all log entries for this order.

        Returns
        -------
        list[Entry]
            A copy of all log entries.
        """
        return self._log.copy()
    
    def save(self) -> None:
        """
        Save the order to local storage as a pickle file.

        Returns
        -------
        None
        """
        file_path = join(self.__DATA_PATH, f"{self.ID}.pkl")
        with open(file_path, "wb") as file:
            pickle.dump(self, file, protocol=4)

    @classmethod
    def from_ID(cls, order_ID) -> Order:
        """
        Load an order from storage by its ID.

        Parameters
        ----------
        order_ID : str
            The ID of the order to load.

        Returns
        -------
        Order
            The loaded Order object.

        Raises
        ------
        FileNotFoundError
            If no order with the specified ID exists.
        """
        file_path = join(cls.__DATA_PATH, f"{order_ID}.pkl")
        if not isfile(file_path):
            raise FileNotFoundError(f"There's no order with the specifed ID: {order_ID}")
            
        with open(file_path, "rb") as file:
            instance = pickle.load(file)
        
        return instance
    
    
class SizeClass(Enum):
    """
    Enum defining package size classifications and their fee values.
    
    Values represent fee amounts based on package dimensions.
    """
    envelope = 60
    small_box = 120
    medium_box = 250
    big_box = 450
    
class WeightClass(Enum):
    """
    Enum defining package weight classifications and their fee values.
    
    Values represent fee amounts based on package weight.
    """
    extra_light = 60
    light = 120
    heavy = 250
    extra_heavy = 450
    
class Service(Enum):
    """
    Enum defining delivery service types and their fee multipliers.
    
    over_night: Next day delivery (1 day)
    express: Fast delivery (2 days)
    standard: Regular delivery (7 days)
    economy: Budget delivery (14 days)
    """
    over_night = 2.5
    express = 1.8
    standard = 1.2
    economy = 1.0
    
    @property
    def day(self) -> int:
        """
        Get the number of days before deadline after collection.

        Returns
        -------
        int
            The days before the deadline after collection.
        """
        if self is Service.over_night:
            return 1
        elif self is Service.express:
            return 2
        elif self is Service.standard:
            return 7
        elif self is Service.economy:
            return 14
        
class Status(Enum):
    """
    Enum defining order status values.
    
    normal: Order is in progress
    delivered: Package has been delivered
    delayed: Delivery is delayed
    broken: Package was damaged
    missing: Package is lost
    """
    normal = 0
    delivered = 1
    delayed = 2
    broken = 3
    missing = 4
    
if __name__ == "__main__":
    print(Service.over_night.value)