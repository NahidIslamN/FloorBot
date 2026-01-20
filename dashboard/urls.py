from django.urls import path
from .views import *

urlpatterns = [
    path('products/', Catalogs_Views.as_view()),
    path('products/<int:pk>/', Catalogs_Views.as_view()),
    path('wallet-ballence/', StripeWalletBalance.as_view(), name='stripe-balance'),
    path('feed-backs/', CustomerFeedBacke.as_view(), name='feedbackd')
    
]
