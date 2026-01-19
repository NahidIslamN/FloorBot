from django.urls import path
from .views import *

urlpatterns = [

    path('products/', ProductsView.as_view(), name='all-products'),
    path('searchsuggestion/', SearchSuggestion.as_view(), name='search-suggestion'),

    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    path('category-products/<int:category_id>/', CategoryProductsView.as_view(), name='category-products'),
    path('categories/', Categoriesview.as_view(), name='category-products'),
    path('orders/', User_Ordedrs.as_view(), name='orders'),
    path('delevard-orders/', User_Complete_Ordedrs.as_view(), name="deliverd_orders")

]
