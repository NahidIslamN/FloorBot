from django.db import models
from auths.models import CustomUser
from decimal import Decimal

# Create your models here.

class Images(models.Model):
    title = models. CharField(null=True, blank=True)
    image = models.ImageField(upload_to='products')


class SubCategory(models.Model):
    title = models.CharField(unique=True)


class Category(models.Model):
    title = models.CharField(unique=True)
    image  = models.ImageField(upload_to='categoris')
    def __str__(self):
        return self.title



class Product(models.Model):
    product_title = models.CharField(max_length=250)
    brand_manufacturer = models.CharField(max_length=250)
    item_description = models.TextField(default='')
    main_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.TextField(default='')

    #uplodes
    images = models.ManyToManyField(Images, related_name='images',blank=True)
    primary_image = models.ImageField(upload_to='products')

    #pricing data
    regular_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    sale_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    tax_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    # delivary_fee = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    product_id = models.CharField(max_length=250, unique=True)
    pack_coverage = models.CharField(max_length=250)

    #Item Dimensions
    length = models.CharField(max_length=250)
    width = models.CharField(max_length=250)
    thickness = models.CharField(max_length=250)
    weight = models.CharField(max_length=250)
    installation_method = models.CharField(max_length=250)
    coverage_per_pack = models.CharField(max_length=250)

    #Categorized Details
    pile_height = models.CharField(max_length=250, null=True, blank=True)
    materials = models.TextField(blank=True)
    format = models.CharField(max_length=250, null=True, blank=True)
    is_underlay_required = models.BooleanField(default=False, null=True, blank=True)
    available_colors = models.TextField(blank=True)
    pattern_type = models.CharField(max_length=250, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0, null=True, blank=True)

    is_calculate = models.BooleanField(default=False)

    return_policy = models.TextField(default="30-day return policy. Items must be in original condition with packaging. Return shipping costs may apply.")

    # Best Salse
    total_salses = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product_title



class OrderTable(models.Model):
    ORDER_STATUS = (
        ('placed', "Placed"),
        ('in_transit', 'In transit'),
        ('delivered', 'Delivered'),
        ('cancelled', "Cancelled"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    delivery_fee = models.DecimalField(default=0.00, decimal_places=2, max_digits=9)
    tax_fee = models.DecimalField(default=0.00, decimal_places=2, max_digits=9)
    order_total = models.DecimalField(default=0.00, decimal_places=2, max_digits=9)

    ship_method = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=250, choices=ORDER_STATUS, default='placed')
    carrier = models.CharField(max_length=250, null=True, blank=True)
    tracking_no = models.CharField(unique=True, null=True, blank=True)

    is_paid = models.BooleanField(default=False)
   
    paid_ammount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    is_shiped = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ### adresss
    country_or_region = models.CharField(max_length=250, null=True, blank=True)
    address_line_i = models.CharField(max_length=250, null=True, blank=True)
    address_line_ii = models.CharField(max_length=250, null=True, blank=True)
    suburb = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    postal_code = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)

    custormer_feedback = models.TextField(blank=True, null=True)
    is_feedbacked = models.BooleanField(default=False)


    def calculate_order_total(self):
        """Calculate total based on sale or regular price"""
        # Base price
        base_price = self.product.sale_price if self.product.sale_price > 0 else self.product.regular_price

        # Safely handle delivery_fee and tax_fee
        delivery_fee = self.delivery_fee or Decimal('0.00')
        tax_fee = self.tax_fee or Decimal('0.00')

        total_price = Decimal(base_price) + Decimal(delivery_fee) + Decimal(tax_fee)

        return total_price * self.quantity




    def save(self, *args, **kwargs):
        self.order_total = self.calculate_order_total()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

    