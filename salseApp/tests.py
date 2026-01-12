from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from dashboard.models import Product, Category
from auths.models import CustomUser

class ProductViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(title="Test Category")
        
        # Create 150 products to test pagination
        for i in range(150):
            Product.objects.create(
                product_title=f"Product {i}",
                brand_manufacturer="Brand",
                product_id=f"PID{i}",
                regular_price=100.00,
                sale_price=90.00,
                main_category=self.category,
                total_salses=i
            )

    def test_all_products_pagination(self):
        response = self.client.get('/users/all-products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 100)
        self.assertEqual(response.data['meta']['total_items'], 150)
        self.assertEqual(response.data['meta']['total_pages'], 2)
        self.assertEqual(response.data['meta']['current_page'], 1)

    def test_best_products_ordering(self):
        response = self.client.get('/users/best-products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Higher total_salses should come first (149, 148, ...)
        self.assertEqual(response.data['data'][0]['product_title'], "Product 149")

    def test_product_detail(self):
        product = Product.objects.first()
        response = self.client.get(f'/users/product-detail/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['product_title'], product.product_title)

    def test_category_products(self):
        response = self.client.get(f'/users/category-products/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['meta']['total_items'], 150)
