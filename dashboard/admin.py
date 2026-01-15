from django.contrib import admin
from .models import Product, Category,Images, OrderTable


# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Images)
admin.site.register(OrderTable)

