"""
Order Calculator - Calculates quantities, areas, and pricing for flooring orders
"""
from typing import Dict, List, Optional
from ai_app.schemas import ProductInfo, OrderItem, OrderSummary
from ai_app.product_service import DjangoProductService


class OrderCalculator:
    """Handles order calculations and pricing"""
    
    def __init__(self, product_service: DjangoProductService):
        """Initialize calculator with product service"""
        self.product_service = product_service
    
    def calculate_area(self, width: float, length: float) -> float:
        """Calculate area in square meters"""
        return width * length
    
    def calculate_quantity_needed(self, area: float, product: ProductInfo) -> float:
        """Calculate quantity needed based on area and product coverage"""
        if product.unit == "box":
            boxes_needed = area / product.coverage_per_unit
            return round(boxes_needed + 0.5)
        else:
            return round(area, 2)
    
    def calculate_order_item(self, product_id: str, quantity: float, area: Optional[float] = None) -> Optional[OrderItem]:
        """
        Calculate order item details
        
        Args:
            product_id: Product ID
            quantity: Quantity to order
            area: Optional area covered (calculated if not provided)
            
        Returns:
            OrderItem with pricing details
        """
        product = self.product_service.get_product_by_id(product_id)
        
        if not product:
            return None
        
        price = product.sale_price if product.sale_price > 0 else product.price_per_unit
        
        area_covered = area or (quantity * product.coverage_per_unit)
        
        subtotal = price * quantity
        discount_amount = subtotal * (product.discount_percentage / 100)
        total = subtotal - discount_amount
        
        return OrderItem(
            product=product,
            quantity=quantity,
            area_covered=area_covered,
            unit_price=price,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total
        )
    
    def create_order_summary(self, items: List[OrderItem], tax_rate: float = 0.1, delivery_fee: float = 0.0) -> OrderSummary:
        """
        Create complete order summary
        
        Args:
            items: List of order items
            tax_rate: Tax rate (default 10%)
            delivery_fee: Flat delivery fee
            
        Returns:
            OrderSummary with totals
        """
        subtotal = sum(item.subtotal for item in items)
        total_discount = sum(item.discount_amount for item in items)
        
        subtotal_after_discount = subtotal - total_discount
        tax = subtotal_after_discount * tax_rate
        grand_total = subtotal_after_discount + tax + delivery_fee
        
        return OrderSummary(
            items=items,
            subtotal=subtotal,
            total_discount=total_discount,
            tax=tax,
            delivery_fee=delivery_fee,
            grand_total=grand_total
        )
    
    def get_product_recommendations(self, product_type: str, budget: Optional[float] = None) -> List[ProductInfo]:
        """Get product recommendations based on type and budget"""
        products = self.product_service.search_products(product_type=product_type)
        
        if budget:
            products = [p for p in products if (p.sale_price or p.price_per_unit) <= budget]
        
        products.sort(key=lambda p: p.discount_percentage, reverse=True)
        
        return products[:5]
