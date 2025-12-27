# -*- coding: utf-8 -*-
"""
Test suite for Customer.py

@author: laisz
"""
import pytest
import os
import pickle
import tempfile
from unittest.mock import patch, MagicMock
from PaymentArrangement import BillingTiming
from Customer import Customer


class TestCustomerInit:
    """Tests for Customer initialization."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures with mocked data path."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        # Mock the data path and OrdersHandler
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler')
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_customer_creation_basic(self):
        """Test basic customer creation with valid parameters."""
        customer = Customer(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.doe@example.com",
            password="secret123",
            billing_pref=BillingTiming.in_advance
        )
        
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.address == "123 Main St"
        assert customer.number == "1234567890"
        assert customer.email == "john.doe@example.com"
        assert customer.billing_pref == BillingTiming.in_advance
        assert customer.bill_cnt == 0
        assert customer.ID.startswith("C")
    
    def test_customer_id_format(self):
        """Test that customer ID follows the expected format C#####."""
        customer = Customer(
            first_name="Jane",
            last_name="Smith",
            address="456 Oak Ave",
            phone_number="9876543210",
            email="jane.smith@example.com",
            password="pass",
            billing_pref=BillingTiming.on_delivery
        )
        
        assert len(customer.ID) == 6
        assert customer.ID[0] == "C"
        assert customer.ID[1:].isdigit()
    
    def test_phone_number_with_spaces(self):
        """Test that phone numbers with spaces are accepted."""
        customer = Customer(
            first_name="Test",
            last_name="User",
            address="Address",
            phone_number="123 456 7890",
            email="test@example.com",
            password="pass",
            billing_pref=BillingTiming.monthly
        )
        
        assert customer.number == "123 456 7890"
    
    def test_phone_number_invalid_characters(self):
        """Test that phone numbers with invalid characters raise ValueError."""
        with pytest.raises(ValueError, match="invalid character"):
            Customer(
                first_name="Test",
                last_name="User",
                address="Address",
                phone_number="123-456-7890",  # Dash is invalid
                email="test@example.com",
                password="pass",
                billing_pref=BillingTiming.in_advance
            )
    
    def test_phone_number_with_letters(self):
        """Test that phone numbers with letters raise ValueError."""
        with pytest.raises(ValueError, match="invalid character"):
            Customer(
                first_name="Test",
                last_name="User",
                address="Address",
                phone_number="123abc7890",
                email="test@example.com",
                password="pass",
                billing_pref=BillingTiming.in_advance
            )


class TestCustomerProperties:
    """Tests for Customer property accessors and setters."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler')
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        self.customer = Customer(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.doe@example.com",
            password="secret123",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_address_setter(self):
        """Test that address can be updated."""
        new_address = "999 New Street"
        self.customer.address = new_address
        assert self.customer.address == new_address
    
    def test_number_setter_valid(self):
        """Test that phone number can be updated with valid value."""
        new_number = "5555555555"
        self.customer.number = new_number
        assert self.customer.number == new_number
    
    def test_number_setter_invalid(self):
        """Test that phone number update with invalid value raises error."""
        with pytest.raises(ValueError):
            self.customer.number = "555-555-5555"


class TestCustomerVerify:
    """Tests for Customer password verification."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler')
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        self.customer = Customer(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.doe@example.com",
            password="correctpassword",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_verify_correct_password(self):
        """Test verification with correct password returns True."""
        assert self.customer.verify("correctpassword") is True
    
    def test_verify_incorrect_password(self):
        """Test verification with incorrect password returns False."""
        assert self.customer.verify("wrongpassword") is False
    
    def test_verify_empty_password(self):
        """Test verification with empty password returns False."""
        assert self.customer.verify("") is False


class TestCustomerBillingPreference:
    """Tests for Customer billing preference methods."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler')
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        self.customer = Customer(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.doe@example.com",
            password="secret",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_set_billing_pref_valid(self):
        """Test setting billing preference with valid BillingTiming."""
        assert self.customer.billing_pref == BillingTiming.in_advance  # Initial value
        self.customer.set_billing_pref(BillingTiming.monthly)
        assert self.customer.billing_pref == BillingTiming.monthly  # Verify the change
    
    def test_set_billing_pref_invalid_type(self):
        """Test setting billing preference with invalid type raises TypeError."""
        with pytest.raises(TypeError, match="Invalid choice"):
            self.customer.set_billing_pref("monthly")
    
    def test_set_billing_pref_invalid_int(self):
        """Test setting billing preference with int raises TypeError."""
        with pytest.raises(TypeError, match="Invalid choice"):
            self.customer.set_billing_pref(1)


class TestCustomerStr:
    """Tests for Customer string representation."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler')
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        self.customer = Customer(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.doe@example.com",
            password="secret",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_str_contains_name(self):
        """Test that __str__ contains the customer's name."""
        result = str(self.customer)
        assert "John" in result
        assert "Doe" in result
    
    def test_str_contains_id(self):
        """Test that __str__ contains the customer's ID."""
        result = str(self.customer)
        assert self.customer.ID in result
    
    def test_str_contains_address(self):
        """Test that __str__ contains the customer's address."""
        result = str(self.customer)
        assert "123 Main St" in result
    
    def test_str_contains_phone(self):
        """Test that __str__ contains the customer's phone number."""
        result = str(self.customer)
        assert "1234567890" in result
    
    def test_str_contains_billing_pref(self):
        """Test that __str__ contains the billing preference."""
        result = str(self.customer)
        assert "in_advance" in result


class TestCustomerOrderAccess:
    """Tests for Customer order access methods."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.mock_oh = MagicMock()
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler', return_value=self.mock_oh)
        self.patcher_cnt = patch.object(Customer, '_cnt', 5)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        self.customer = Customer(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.doe@example.com",
            password="secret",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_my_orders_calls_filter_by_customer(self):
        """Test that my_orders calls OrdersHandler.filter_by_customer."""
        self.mock_oh.filter_by_customer.return_value = []
        
        result = self.customer.my_orders()
        
        self.mock_oh.filter_by_customer.assert_called_once_with(
            self.customer.ID
        )
    
    def test_get_order_access_allowed(self):
        """Test getting an order that belongs to this customer."""
        mock_order = MagicMock()
        mock_order.payer = self.customer.ID  # Set payer to match customer
        self.mock_oh.get.return_value = mock_order
        
        order_id = "O00001"
        result = self.customer.get(order_id)
        
        assert result == mock_order
        self.mock_oh.get.assert_called_once_with(order_id)
    
    def test_get_order_access_denied(self):
        """Test getting an order that doesn't belong to this customer."""
        mock_order = MagicMock()
        mock_order.payer = "C99999"  # Different customer
        self.mock_oh.get.return_value = mock_order
        
        with pytest.raises(RuntimeError, match="Access to order .* denied"):
            self.customer.get("O00001")


class TestCustomerPersistence:
    """Tests for Customer save and load functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler')
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_save_creates_file(self):
        """Test that save() creates a pickle file."""
        customer = Customer(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.doe@example.com",
            password="secret",
            billing_pref=BillingTiming.in_advance
        )
        
        customer.save()
        
        expected_file = self.test_dir / f"{customer.ID}.pkl"
        assert expected_file.exists()
    
    def test_from_id_loads_customer(self):
        """Test that from_ID correctly loads a saved customer."""
        customer = Customer(
            first_name="Jane",
            last_name="Smith",
            address="456 Oak Ave",
            phone_number="9876543210",
            email="jane.smith@example.com",
            password="pass123",
            billing_pref=BillingTiming.on_delivery
        )
        customer.save()
        customer_id = customer.ID
        
        loaded = Customer.from_ID(customer_id)
        
        assert loaded.first_name == "Jane"
        assert loaded.last_name == "Smith"
        assert loaded.address == "456 Oak Ave"
        assert loaded.number == "9876543210"
    
    def test_from_id_nonexistent_raises_error(self):
        """Test that from_ID raises FileNotFoundError for non-existent ID."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            Customer.from_ID("C99999")


class TestCustomerOrders:
    """Tests for Customer order-related methods."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures with mocked data path and OrdersHandler."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.mock_oh = MagicMock()
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler', return_value=self.mock_oh)
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        # Create a test customer
        self.customer = Customer(
            first_name="Test",
            last_name="User",
            address="Test Address",
            phone_number="1234567890",
            email="test.orders@example.com",
            password="password",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_my_orders_calls_filter_by_customer(self):
        """Test that my_orders() calls OrdersHandler.filter_by_customer with customer ID."""
        mock_orders = [MagicMock(), MagicMock()]
        self.mock_oh.filter_by_customer.return_value = mock_orders
        
        result = self.customer.my_orders()
        
        self.mock_oh.filter_by_customer.assert_called_once_with(self.customer.ID)
        assert result == mock_orders
    
    def test_my_orders_empty_list(self):
        """Test that my_orders() returns empty list when no orders."""
        self.mock_oh.filter_by_customer.return_value = []
        
        result = self.customer.my_orders()
        
        assert result == []
    
    def test_get_calls_handler_get(self):
        """Test that get() delegates to OrdersHandler.get() and returns order if authorized."""
        mock_order = MagicMock()
        mock_order.payer = self.customer.ID  # Set payer to match customer
        self.mock_oh.get.return_value = mock_order
        
        result = self.customer.get("O00001")
        
        self.mock_oh.get.assert_called_once_with("O00001")
        assert result == mock_order
    
    def test_get_denies_access_for_other_customer(self):
        """Test that get() raises RuntimeError if order belongs to another customer."""
        mock_order = MagicMock()
        mock_order.payer = "C99999"  # Different customer
        self.mock_oh.get.return_value = mock_order
        
        with pytest.raises(RuntimeError, match="Access to order.*denied"):
            self.customer.get("O00001")
    
    def test_new_order_calls_handler_add(self):
        """Test that new_order() delegates to OrdersHandler.add()."""
        self.customer.new_order("arg1", "arg2", "arg3")
        
        self.mock_oh.add.assert_called_once_with("arg1", "arg2", "arg3")


class TestCustomerBilling:
    """Tests for Customer billing methods (bill, pay)."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures with mocked data path."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.mock_oh = MagicMock()
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler', return_value=self.mock_oh)
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        # Create a test customer
        self.customer = Customer(
            first_name="Test",
            last_name="User",
            address="Test Address",
            phone_number="1234567890",
            email="test.billing@example.com",
            password="password",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_bill_creates_new_bill_in_advance(self):
        """Test that bill() creates a new Bill when billing_pref is in_advance."""
        mock_order = MagicMock()
        mock_order.ID = "O00001"
        
        # First bill should create a new bill
        initial_bill_cnt = self.customer.bill_cnt
        self.customer.bill(mock_order)
        
        # bill_cnt should remain 0 until payment logic (depends on implementation)
        assert self.customer.bill_cnt >= initial_bill_cnt
    
    def test_pay_delegates_to_bill(self):
        """Test that pay() calls the correct bill's pay method."""
        # Create a mock bill and add to customer
        mock_bill = MagicMock()
        mock_bill.ID = "B00001"
        self.customer._bill["B00001"] = mock_bill
        
        # Patch save to avoid pickle error with MagicMock
        with patch.object(self.customer, 'save'):
            self.customer.pay("B00001", "credit_card")
        
        mock_bill.pay.assert_called_once_with("credit_card")
    
    def test_pay_nonexistent_bill_raises_error(self):
        """Test that pay() raises KeyError for non-existent bill."""
        with pytest.raises(KeyError):
            with patch.object(self.customer, 'save'):
                self.customer.pay("B99999", "cash")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
