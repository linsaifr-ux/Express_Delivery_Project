
import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
from datetime import date

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(__file__))

from Staff import Staff, RepoStaff, Driver, CSStaff, Management
# We mock these for the tests
# from Vehicle import Vehicle 
# from Location import Repository

@pytest.fixture
def mock_orders_handler():
    with patch('Staff.OrdersHandler') as MockHandler:
        mock_instance = MagicMock()
        MockHandler.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_vehicle():
    vehicle = MagicMock()
    vehicle.license_plate = "TEST-PLATE"
    vehicle.__str__.return_value = "Test Vehicle"
    return vehicle

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.address = "Test Address"
    repo.__str__.return_value = "Test Repo"
    return repo

class TestStaff:
    def test_init(self):
        s = Staff("John", "Doe", "Driver", "pass")
        assert s.first_name == "John"
        assert s.last_name == "Doe"
        assert s.position == "Driver"
        assert s.verify("pass")
        assert not s.verify("wrong")
        assert s.ID.startswith("S")



    def test_get_order(self, mock_orders_handler):
        s = Staff("Get", "Order", "Pos", "pass")
        s.get("O123")
        mock_orders_handler.get.assert_called_with("O123")


class TestRepoStaff:
    def test_init(self, mock_repo):
        staff = RepoStaff("Alice", "Repo", "RepoStaff", "pass", mock_repo)
        assert staff._repository == mock_repo

    def test_package_at_repo(self, mock_orders_handler, mock_repo):
        staff = RepoStaff("Alice", "Repo", "RepoStaff", "pass", mock_repo)
        staff.package_at_repo()
        mock_orders_handler.filter_by_repo.assert_called_with(mock_repo)

    def test_report_arrival(self, mock_orders_handler, mock_repo):
        staff = RepoStaff("Alice", "Repo", "RepoStaff", "pass", mock_repo)
        mock_order = MagicMock()
        mock_orders_handler.get.return_value = mock_order
        
        staff.report_arrival("O123")
        
        mock_orders_handler.log.assert_called_with("O123", 'A', staff.ID, mock_repo)
        mock_repo.receive.assert_called_with(mock_order)

    def test_report_damage(self, mock_orders_handler, mock_repo):
        staff = RepoStaff("Alice", "Repo", "RepoStaff", "pass", mock_repo)
        staff.report_damage("O123", "Crushed")
        mock_orders_handler.log.assert_called_with("O123", 'C', staff.ID, "Damage Reported", "Crushed")

    def test_report_lost(self, mock_orders_handler, mock_repo):
        staff = RepoStaff("Alice", "Repo", "RepoStaff", "pass", mock_repo)
        staff.report_lost("O123", "Missing")
        mock_orders_handler.log.assert_called_with("O123", 'M', staff.ID, "Loss Reported", "Missing")


class TestDriver:
    def test_init(self, mock_vehicle):
        staff = Driver("Bob", "Driver", "Driver", "pass", mock_vehicle)
        assert staff._vehicle == mock_vehicle

    def test_package_on_vehicle(self, mock_orders_handler, mock_vehicle):
        staff = Driver("Bob", "Driver", "Driver", "pass", mock_vehicle)
        staff.package_on_vehicle()
        mock_orders_handler.filter_by_vehicle.assert_called_with(mock_vehicle)

    def test_report_transit(self, mock_orders_handler, mock_vehicle):
        staff = Driver("Bob", "Driver", "Driver", "pass", mock_vehicle)
        mock_order = MagicMock()
        mock_orders_handler.get.return_value = mock_order
        
        staff.report_transit("O123")
        
        mock_orders_handler.log.assert_called_with("O123", 'T', staff.ID, mock_vehicle, mock_order.origin, mock_order.destination)
        mock_vehicle.pick_up.assert_called_with(mock_order)

    def test_report_delivered(self, mock_orders_handler, mock_vehicle):
        staff = Driver("Bob", "Driver", "Driver", "pass", mock_vehicle)
        mock_order = MagicMock()
        mock_orders_handler.get.return_value = mock_order
        
        staff.report_delivered("O123")
        
        mock_orders_handler.log.assert_called_with("O123", 'A', staff.ID, mock_order.destination)
        mock_vehicle.deliver.assert_called_with(mock_order)


class TestCSStaff:
    def test_filter_methods(self, mock_orders_handler):
        staff = CSStaff("Charlie", "CS", "CS", "pass")
        
        staff.filter_by_customer("C123")
        mock_orders_handler.filter_by_customer.assert_called_with("C123")
        
        d1, d2 = date(2025, 1, 1), date(2025, 1, 31)
        staff.filter_by_date(d1, d2)
        mock_orders_handler.filter_by_date.assert_called_with(d1, d2)
        
        staff.filter_delayed()
        mock_orders_handler.filter_delayed.assert_called()


class TestManagement:
    def test_filter_methods(self, mock_orders_handler, mock_vehicle, mock_repo):
        staff = Management("Boss", "Man", "Mgr", "pass")
        
        staff.filter_by_vehicle(mock_vehicle)
        mock_orders_handler.filter_by_vehicle.assert_called_with(mock_vehicle)
        
        staff.filter_by_repo(mock_repo)
        mock_orders_handler.filter_by_repo.assert_called_with(mock_repo)

    def test_add_vehicle(self):
        staff = Management("Boss", "Man", "Mgr", "pass")
        
        v1 = staff.add_vehicle("Minivan", "ABC-123")
        assert "minivan" in str(v1)
        
        v2 = staff.add_vehicle("Truck", "TRK-999")
        assert "truck" in str(v2)
        
        v3 = staff.add_vehicle("MiniTruck", "MINI-000")
        assert "mini truck" in str(v3)

    def test_add_repo(self):
        staff = Management("Boss", "Man", "Mgr", "pass")
        repo = staff.add_repo("123 St", "Repo Name")
        assert repo.address == "123 St"
        assert repo.name == "Repo Name"
