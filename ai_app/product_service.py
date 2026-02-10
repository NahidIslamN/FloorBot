"""
Product Service - Bridges AI chatbot with Django Product model
"""
from typing import List, Optional, Dict, Any
from django.db.models import Q
from dashboard.models import Product
from ai_app.schemas import ProductInfo


class DjangoProductService:
    """
    Product service that works with Django Product model
    Provides products from the actual database
    """
    
    def search_products(self, 
                       product_type: Optional[str] = None,
                       color: Optional[str] = None,
                       material: Optional[str] = None,
                       min_price: Optional[float] = None,
                       max_price: Optional[float] = None) -> List[ProductInfo]:
        """
        Search for products based on criteria
        
        Args:
            product_type: Product category (carpets, vinyl, laminate, wood flooring)
            color: Product color
            material: Material type
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            List of ProductInfo objects
        """
        queryset = Product.objects.filter(stock_quantity__gt=0)
        
        if product_type:
            category_map = {
                "carpets": ["carpet", "carpets", "rug"],
                "vinyl": ["vinyl", "lvt", "luxury vinyl"],
                "laminate": ["laminate"],
                "wood flooring": ["wood", "hardwood", "engineered wood", "timber"]
            }
            
            category_keywords = category_map.get(product_type.lower(), [product_type.lower()])
            
            category_query = Q()
            for keyword in category_keywords:
                category_query |= Q(main_category__title__icontains=keyword)
                category_query |= Q(product_title__icontains=keyword)
                category_query |= Q(item_description__icontains=keyword)
            
            queryset = queryset.filter(category_query)
        
        if color:
            queryset = queryset.filter(
                Q(available_colors__icontains=color) |
                Q(product_title__icontains=color) |
                Q(item_description__icontains=color)
            )
        
        if material:
            queryset = queryset.filter(
                Q(materials__icontains=material) |
                Q(product_title__icontains=material)
            )
        
        if min_price is not None:
            queryset = queryset.filter(
                Q(sale_price__gte=min_price) | Q(regular_price__gte=min_price)
            )
        
        if max_price is not None:
            queryset = queryset.filter(
                Q(sale_price__lte=max_price) | Q(regular_price__lte=max_price)
            )
        
        products = queryset[:10]
        
        return [self._convert_to_product_info(p) for p in products]
    
    def get_product_by_id(self, product_id: str) -> Optional[ProductInfo]:
        """Get a specific product by ID"""
        try:
            product = Product.objects.get(product_id=product_id)
            return self._convert_to_product_info(product)
        except Product.DoesNotExist:
            return None
    
    def get_all_products(self, limit: int = 50) -> List[ProductInfo]:
        """Get all available products"""
        products = Product.objects.filter(stock_quantity__gt=0)[:limit]
        return [self._convert_to_product_info(p) for p in products]
    
    def _convert_to_product_info(self, product: Product) -> ProductInfo:
        """Convert Django Product model to ProductInfo schema"""
        
        coverage = self._parse_coverage(product.coverage_per_pack)
        
        discount_pct = 0
        if product.sale_price and product.regular_price:
            if product.sale_price < product.regular_price:
                discount_pct = ((product.regular_price - product.sale_price) / product.regular_price) * 100
        
        unit = "m2"
        if "box" in product.coverage_per_pack.lower() or "pack" in product.coverage_per_pack.lower():
            unit = "box"
        
        return ProductInfo(
            id=product.product_id,
            name=product.product_title,
            category=self._get_category_type(product),
            color=self._extract_color(product),
            material=product.materials or "",
            price_per_unit=float(product.regular_price),
            sale_price=float(product.sale_price) if product.sale_price else 0,
            unit=unit,
            coverage_per_unit=coverage,
            stock_quantity=product.stock_quantity or 0,
            discount_percentage=round(discount_pct, 2),
            description=product.item_description or "",
            specifications={
                "length": product.length,
                "width": product.width,
                "thickness": product.thickness,
                "weight": product.weight,
                "installation_method": product.installation_method,
                "pile_height": product.pile_height or "",
                "format": product.format or "",
                "pattern_type": product.pattern_type or "",
                "underlay_required": product.is_underlay_required
            }
        )
    
    def _get_category_type(self, product: Product) -> str:
        """Extract category type from product"""
        if product.main_category:
            title = product.main_category.title.lower()
            if "carpet" in title or "rug" in title:
                return "carpets"
            elif "vinyl" in title or "lvt" in title:
                return "vinyl"
            elif "laminate" in title:
                return "laminate"
            elif "wood" in title or "timber" in title or "hardwood" in title:
                return "wood flooring"
        
        title = product.product_title.lower()
        if "carpet" in title:
            return "carpets"
        elif "vinyl" in title:
            return "vinyl"
        elif "laminate" in title:
            return "laminate"
        elif "wood" in title:
            return "wood flooring"
        
        return "flooring"
    
    def _extract_color(self, product: Product) -> str:
        """Extract primary color from product"""
        if product.available_colors:
            colors = product.available_colors.split(',')
            if colors:
                return colors[0].strip()
        
        common_colors = ["grey", "gray", "beige", "brown", "white", "black", "oak", "walnut", 
                        "natural", "dark", "light", "cream", "tan", "charcoal"]
        
        title = product.product_title.lower()
        for color in common_colors:
            if color in title:
                return color.capitalize()
        
        return "Natural"
    
    def _parse_coverage(self, coverage_str: str) -> float:
        """Parse coverage from string format"""
        if not coverage_str:
            return 1.0
        
        import re
        numbers = re.findall(r'\d+\.?\d*', coverage_str)
        
        if numbers:
            return float(numbers[0])
        
        return 1.0
