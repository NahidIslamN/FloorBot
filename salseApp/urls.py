from django.urls import path
from .views import *

urlpatterns = [
    path('all-products/', ProductsView.as_view(), name='all-products'),
    path('newest-products/', NewestProducts.as_view(), name='newest-products'),
    path('best-products/', BestProducts.as_view(), name='best-products'),
    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('category-products/<int:category_id>/', CategoryProductsView.as_view(), name='category-products'),
    path('categories/', Categoriesview.as_view(), name='category-products'),
]
