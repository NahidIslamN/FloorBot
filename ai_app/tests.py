"""
Simple tests for AI functionality
"""
from django.test import TestCase
from ai_app.api import FloorBotAPI
from ai_app.session_manager import SessionManager
from ai_app.product_service import DjangoProductService


class AISessionTestCase(TestCase):
    """Test AI session management"""
    
    def setUp(self):
        """Set up test case"""
        self.session_manager = SessionManager()
    
    def test_create_session(self):
        """Test session creation"""
        session = self.session_manager.create_session()
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.session_id)
    
    def test_get_session(self):
        """Test session retrieval"""
        session = self.session_manager.create_session()
        retrieved = self.session_manager.get_session(session.session_id)
        self.assertEqual(session.session_id, retrieved.session_id)
    
    def test_delete_session(self):
        """Test session deletion"""
        session = self.session_manager.create_session()
        self.session_manager.delete_session(session.session_id)
        retrieved = self.session_manager.get_session(session.session_id)
        self.assertIsNone(retrieved)


class ProductServiceTestCase(TestCase):
    """Test product service"""
    
    def setUp(self):
        """Set up test case"""
        self.product_service = DjangoProductService()
    
    def test_search_products(self):
        """Test product search"""
        products = self.product_service.search_products(product_type="carpets")
        self.assertIsInstance(products, list)
    
    def test_get_all_products(self):
        """Test getting all products"""
        products = self.product_service.get_all_products(limit=10)
        self.assertIsInstance(products, list)
