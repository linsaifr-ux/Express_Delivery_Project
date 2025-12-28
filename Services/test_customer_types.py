# -*- coding: utf-8 -*-
"""
Test suite for CustomerTypes.py (Normal, Contracted, Sponsored)

@author: laisz
"""
import pytest
from unittest.mock import patch, MagicMock
from PaymentArrangement import BillingTiming, PaymentMethod
from Customer import Customer
from CustomerTypes import Normal, Contracted, Sponsored


class TestNormalInit:
    """Tests for Normal customer initialization."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures with mocked data path."""
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
    
    def test_normal_creation_without_card(self):
        """Test Normal customer creation without initial card."""
        customer = Normal(
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            phone_number="1234567890",
            email="john.normal@example.com",
            password="secret",
            billing_pref=BillingTiming.in_advance
        )
        
        assert customer.first_name == "John"
        assert customer.card == []
        assert customer.billing_pref == BillingTiming.in_advance
    
    def test_normal_creation_with_card(self):
        """Test Normal customer creation with initial card."""
        customer = Normal(
            first_name="Jane",
            last_name="Doe",
            address="456 Oak Ave",
            phone_number="9876543210",
            email="jane.normal@example.com",
            password="secret",
            billing_pref=BillingTiming.on_delivery,
            card="4111111111111111"
        )
        
        assert customer.card == ["4111111111111111"]


class TestNormalCard:
    """Tests for Normal customer card management."""
    
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
        
        self.customer = Normal(
            first_name="Test",
            last_name="User",
            address="Address",
            phone_number="1234567890",
            email="test.card@example.com",
            password="pass",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_add_card(self):
        """Test adding a card to Normal customer."""
        self.customer.add_card("4111111111111111")
        
        assert "4111111111111111" in self.customer.card
    
    def test_add_multiple_cards(self):
        """Test adding multiple cards."""
        self.customer.add_card("4111111111111111")
        self.customer.add_card("5500000000000004")
        
        cards = self.customer.card
        assert len(cards) == 2
        assert "4111111111111111" in cards
        assert "5500000000000004" in cards
    
    def test_card_returns_copy(self):
        """Test that card property returns a copy."""
        self.customer.add_card("4111111111111111")
        
        cards = self.customer.card
        cards.append("MODIFIED")
        
        # Original should not be modified
        assert "MODIFIED" not in self.customer.card


class TestNormalNewOrder:
    """Tests for Normal customer new_order validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.mock_oh = MagicMock()
        self.mock_oh.add.return_value = "O0000000000001"
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler', return_value=self.mock_oh)
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_cnt.start()
        
        self.customer = Normal(
            first_name="Test",
            last_name="User",
            address="Address",
            phone_number="1234567890",
            email="test.order@example.com",
            password="pass",
            billing_pref=BillingTiming.in_advance
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_new_order_with_in_advance(self):
        """Test new_order accepts in_advance billing timing."""
        order_id = self.customer.new_order(BillingTiming.in_advance, "arg2", "arg3")
        
        assert order_id == "O0000000000001"
    
    def test_new_order_with_on_delivery(self):
        """Test new_order accepts on_delivery billing timing."""
        order_id = self.customer.new_order(BillingTiming.on_delivery, "arg2", "arg3")
        
        assert order_id == "O0000000000001"
    
    def test_new_order_rejects_monthly(self):
        """Test new_order rejects monthly billing timing."""
        with pytest.raises(ValueError, match="in_advance or on_delivery"):
            self.customer.new_order(BillingTiming.monthly, "arg2", "arg3")


class TestNormalPay:
    """Tests for Normal customer pay validation."""
    
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
        
        self.customer = Normal(
            first_name="Test",
            last_name="User",
            address="Address",
            phone_number="1234567890",
            email="test.pay@example.com",
            password="pass",
            billing_pref=BillingTiming.in_advance
        )
        
        # Add a mock bill
        self.mock_bill = MagicMock()
        self.customer._bill["B00001"] = self.mock_bill
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_pay_accepts_card(self):
        """Test pay accepts card payment method."""
        with patch.object(self.customer, 'save'):
            self.customer.pay("B00001", "TX001", PaymentMethod.card)
        
        self.mock_bill.pay.assert_called_once()
    
    def test_pay_accepts_cash(self):
        """Test pay accepts cash payment method."""
        with patch.object(self.customer, 'save'):
            self.customer.pay("B00001", "TX001", PaymentMethod.cash)
        
        self.mock_bill.pay.assert_called_once()
    
    def test_pay_rejects_wire(self):
        """Test pay rejects wire payment method."""
        with pytest.raises(ValueError, match="card or cash"):
            self.customer.pay("B00001", "TX001", PaymentMethod.wire)


class TestContractedInit:
    """Tests for Contracted customer initialization."""
    
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
    
    def test_contracted_creation(self):
        """Test Contracted customer creation."""
        customer = Contracted(
            first_name="Business",
            last_name="Corp",
            address="789 Corporate Blvd",
            phone_number="5555555555",
            email="business@corp.com",
            password="secure",
            account="ACC-12345"
        )
        
        assert customer.first_name == "Business"
        assert customer.account == "ACC-12345"
        assert customer.billing_pref == BillingTiming.monthly
    
    def test_contracted_billing_pref_always_monthly(self):
        """Test that Contracted always has monthly billing preference."""
        customer = Contracted(
            first_name="Test",
            last_name="Business",
            address="Address",
            phone_number="1234567890",
            email="test.contracted@example.com",
            password="pass",
            account="ACC-00001"
        )
        
        # Billing preference is hardcoded to monthly
        assert customer.billing_pref == BillingTiming.monthly


class TestContractedAccount:
    """Tests for Contracted customer account management."""
    
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
        
        self.customer = Contracted(
            first_name="Test",
            last_name="Business",
            address="Address",
            phone_number="1234567890",
            email="test.account@example.com",
            password="pass",
            account="ACC-INITIAL"
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_account_getter(self):
        """Test account property getter."""
        assert self.customer.account == "ACC-INITIAL"
    
    def test_account_setter(self):
        """Test account property setter."""
        self.customer.account = "ACC-UPDATED"
        
        assert self.customer.account == "ACC-UPDATED"


class TestContractedNewOrder:
    """Tests for Contracted customer new_order validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.mock_oh = MagicMock()
        self.mock_oh.add.return_value = "O0000000000001"
        mock_order = MagicMock()
        mock_order.ID = "O0000000000001"
        self.mock_oh.get.return_value = mock_order
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler', return_value=self.mock_oh)
        self.patcher_oh2 = patch('CustomerTypes.OrdersHandler', return_value=self.mock_oh)
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_oh2.start()
        self.patcher_cnt.start()
        
        self.customer = Contracted(
            first_name="Test",
            last_name="Business",
            address="Address",
            phone_number="1234567890",
            email="test.corder@example.com",
            password="pass",
            account="ACC-00001"
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_oh2.stop()
        self.patcher_cnt.stop()
    
    def test_new_order_with_monthly(self):
        """Test new_order accepts monthly billing timing."""
        with patch.object(self.customer, 'bill'):
            order_id = self.customer.new_order(BillingTiming.monthly, "arg2", "arg3")
        
        assert order_id == "O0000000000001"
    
    def test_new_order_rejects_in_advance(self):
        """Test new_order rejects in_advance billing timing."""
        with pytest.raises(ValueError, match="monthly"):
            self.customer.new_order(BillingTiming.in_advance, "arg2", "arg3")
    
    def test_new_order_rejects_on_delivery(self):
        """Test new_order rejects on_delivery billing timing."""
        with pytest.raises(ValueError, match="monthly"):
            self.customer.new_order(BillingTiming.on_delivery, "arg2", "arg3")


class TestContractedPay:
    """Tests for Contracted customer pay (always wire transfer)."""
    
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
        
        self.customer = Contracted(
            first_name="Test",
            last_name="Business",
            address="Address",
            phone_number="1234567890",
            email="test.cpay@example.com",
            password="pass",
            account="ACC-00001"
        )
        
        self.mock_bill = MagicMock()
        self.customer._bill["B00001"] = self.mock_bill
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_pay_uses_wire_transfer(self):
        """Test that pay always uses wire transfer."""
        with patch.object(self.customer, 'save'):
            self.customer.pay("B00001", "TX001")
        
        # Should be called with wire transfer
        self.mock_bill.pay.assert_called_once_with("TX001", PaymentMethod.wire)


class TestSponsoredInit:
    """Tests for Sponsored customer initialization."""
    
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
    
    def test_sponsored_creation(self):
        """Test Sponsored customer creation."""
        # Sponsored uses positional args: sponsor_ID, first_name, last_name, address, phone, email, password, billing_pref
        customer = Sponsored(
            "C00001",  # sponsor_ID
            "Sponsored",  # first_name
            "User",  # last_name
            "123 Sponsored St",  # address
            "1111111111",  # phone_number
            "sponsored@example.com",  # email
            "pass",  # password
            BillingTiming.in_advance  # billing_pref
        )
        
        assert customer.first_name == "Sponsored"
        assert customer.sponsor == "C00001"


class TestSponsoredSponsor:
    """Tests for Sponsored customer sponsor management."""
    
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
        
        # Sponsored uses positional args
        self.customer = Sponsored(
            "C00001",  # sponsor_ID
            "Test",  # first_name
            "Sponsored",  # last_name
            "Address",  # address
            "1234567890",  # phone_number
            "test.sponsor@example.com",  # email
            "pass",  # password
            BillingTiming.in_advance  # billing_pref
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_sponsor_getter(self):
        """Test sponsor property getter."""
        assert self.customer.sponsor == "C00001"
    
    def test_sponsor_setter_valid_contracted(self):
        """Test sponsor setter accepts Contracted customer."""
        # Mock Customer.from_ID to return a Contracted customer
        mock_contracted = MagicMock(spec=Contracted)
        with patch.object(Customer, 'from_ID', return_value=mock_contracted):
            self.customer.sponsor = "C00002"
        
        assert self.customer.sponsor == "C00002"
    
    def test_sponsor_setter_rejects_non_contracted(self):
        """Test sponsor setter rejects non-Contracted customer."""
        # Mock Customer.from_ID to return a Normal customer
        mock_normal = MagicMock(spec=Normal)
        with patch.object(Customer, 'from_ID', return_value=mock_normal):
            with pytest.raises(ValueError, match="Contracted customer"):
                self.customer.sponsor = "C00002"


class TestSponsoredNewOrder:
    """Tests for Sponsored customer new_order validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test fixtures."""
        self.test_dir = tmp_path / "customer"
        self.test_dir.mkdir()
        
        self.mock_oh = MagicMock()
        self.mock_oh.add.return_value = "O0000000000001"
        mock_order = MagicMock()
        mock_order.ID = "O0000000000001"
        self.mock_oh.get.return_value = mock_order
        
        # Mock sponsor
        self.mock_sponsor = MagicMock(spec=Contracted)
        
        self.patcher_path = patch.object(Customer, '_Customer__DATA_PATH', str(self.test_dir))
        self.patcher_oh = patch('Customer.OrdersHandler', return_value=self.mock_oh)
        self.patcher_oh2 = patch('CustomerTypes.OrdersHandler', return_value=self.mock_oh)
        self.patcher_from_id = patch.object(Customer, 'from_ID', return_value=self.mock_sponsor)
        self.patcher_cnt = patch.object(Customer, '_cnt', 0)
        
        self.patcher_path.start()
        self.patcher_oh.start()
        self.patcher_oh2.start()
        self.patcher_from_id.start()
        self.patcher_cnt.start()
        
        # Sponsored uses positional args
        self.customer = Sponsored(
            "C00001",  # sponsor_ID
            "Test",  # first_name
            "Sponsored",  # last_name
            "Address",  # address
            "1234567890",  # phone_number
            "test.sorder@example.com",  # email
            "pass",  # password
            BillingTiming.in_advance  # billing_pref
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_oh2.stop()
        self.patcher_from_id.stop()
        self.patcher_cnt.stop()
    
    def test_new_order_with_in_advance(self):
        """Test new_order accepts in_advance billing timing."""
        order_id = self.customer.new_order(BillingTiming.in_advance, "arg2", "arg3")
        
        assert order_id == "O0000000000001"
    
    def test_new_order_rejects_monthly(self):
        """Test new_order rejects monthly billing timing."""
        with pytest.raises(ValueError, match="in_advance"):
            self.customer.new_order(BillingTiming.monthly, "arg2", "arg3")
    
    def test_new_order_rejects_on_delivery(self):
        """Test new_order rejects on_delivery billing timing."""
        with pytest.raises(ValueError, match="in_advance"):
            self.customer.new_order(BillingTiming.on_delivery, "arg2", "arg3")
    
    def test_new_order_sends_sponsor_notification(self):
        """Test that new_order sends notification to sponsor."""
        self.customer.new_order(BillingTiming.in_advance, "arg2", "arg3")
        
        # Sponsor should be notified
        self.mock_sponsor.notify.assert_called_once()


class TestSponsorshipWorkflow:
    """Integration tests for the sponsorship approval/rejection workflow."""
    
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
        
        # Create a Contracted customer
        self.contracted = Contracted(
            first_name="Sponsor",
            last_name="Corp",
            address="Address",
            phone_number="1234567890",
            email="sponsor@corp.com",
            password="pass",
            account="ACC-00001"
        )
        
        yield
        
        self.patcher_path.stop()
        self.patcher_oh.stop()
        self.patcher_cnt.stop()
    
    def test_approve_sponsor_bills_contracted(self):
        """Test that approve_sponsor bills the Contracted customer."""
        mock_order = MagicMock()
        mock_order.ID = "O00001"
        mock_order.payer = "C00002"  # Sponsored customer ID
        
        mock_sponsored = MagicMock(spec=Sponsored)
        
        with patch.object(Customer, 'from_ID', return_value=mock_sponsored):
            with patch.object(self.contracted, 'bill') as mock_bill:
                self.contracted.approve_sponsor(mock_order)
        
        # Contracted should be billed
        mock_bill.assert_called_once_with(mock_order)
        # Sponsored should be notified
        mock_sponsored.notify.assert_called_once()
    
    def test_reject_sponsor_bills_sponsored(self):
        """Test that reject_sponsor bills the Sponsored customer."""
        mock_order = MagicMock()
        mock_order.ID = "O00001"
        mock_order.payer = "C00002"
        
        mock_sponsored = MagicMock(spec=Sponsored)
        
        with patch.object(Customer, 'from_ID', return_value=mock_sponsored):
            self.contracted.reject_sponsor(mock_order)
        
        # Sponsored should be billed
        mock_sponsored.bill.assert_called_once_with(mock_order)
        # Sponsored should be notified
        mock_sponsored.notify.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
