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
                       max_price: Optional[float] = None,
                       pattern: Optional[str] = None,
                       keyword: Optional[str] = None,
                       limit: int = 10) -> List[ProductInfo]:
        """
        Search for products based on criteria
        
        Args:
            product_type: Product category (carpets, vinyl, laminate, wood flooring)
            color: Product color
            material: Material type
            min_price: Minimum price
            max_price: Maximum price
            pattern: Pattern type (e.g., modern, traditional, rustic)
            keyword: General keyword search across all fields
            limit: Maximum number of results (default 10)
            
        Returns:
            List of ProductInfo objects
        """
        queryset = Product.objects.filter(stock_quantity__gt=0)
        
        # Enhanced product type matching with more keywords and fuzzy matching
        if product_type:
            # Normalize and handle typos/variations
            product_type_normalized = self._normalize_product_type(product_type)
            
            category_map = {
                "carpets": ["carpet", "carpets", "rug", "rugs", "carpat", "carpets"],
                "vinyl": ["vinyl", "lvt", "luxury vinyl", "vinyl tile", "vinyl plank", "vynil"],
                "laminate": ["laminate", "laminated", "laminat"],
                "wood flooring": ["wood", "hardwood", "engineered wood", "timber", "wooden", "oak", "walnut", "wood floor"]
            }
            
            category_keywords = category_map.get(product_type_normalized, [product_type.lower()])
            
            category_query = Q()
            for keyword_item in category_keywords:
                category_query |= Q(main_category__title__icontains=keyword_item)
                category_query |= Q(product_title__icontains=keyword_item)
                category_query |= Q(item_description__icontains=keyword_item)
            
            queryset = queryset.filter(category_query)
        
        # Enhanced color matching with variations
        if color:
            color_variations = self._get_color_variations(color)
            color_query = Q()
            for color_var in color_variations:
                color_query |= Q(available_colors__icontains=color_var)
                color_query |= Q(product_title__icontains=color_var)
                color_query |= Q(item_description__icontains=color_var)
            queryset = queryset.filter(color_query)
        
        if material:
            queryset = queryset.filter(
                Q(materials__icontains=material) |
                Q(product_title__icontains=material)
            )
        
        if pattern:
            queryset = queryset.filter(
                Q(pattern_type__icontains=pattern) |
                Q(product_title__icontains=pattern) |
                Q(item_description__icontains=pattern)
            )
        
        if keyword:
            queryset = queryset.filter(
                Q(product_title__icontains=keyword) |
                Q(item_description__icontains=keyword) |
                Q(materials__icontains=keyword) |
                Q(available_colors__icontains=keyword)
            )
        
        if min_price is not None:
            queryset = queryset.filter(
                Q(sale_price__gte=min_price) | Q(regular_price__gte=min_price)
            )
        
        if max_price is not None:
            queryset = queryset.filter(
                Q(sale_price__lte=max_price) | Q(regular_price__lte=max_price)
            )
        
        # Limit results to avoid overwhelming users
        products = queryset[:limit]
        
        return [self._convert_to_product_info(p) for p in products]
    
    def _normalize_product_type(self, product_type: str) -> str:
        """Normalize product type to handle typos and variations"""
        product_type = product_type.lower().strip()
        
        # Common typos and variations
        typo_map = {
            "carpat": "carpets",
            "carpets": "carpets",
            "carpet": "carpets",
            "rug": "carpets",
            "rugs": "carpets",
            "vynil": "vinyl",
            "vinly": "vinyl",
            "vinyl": "vinyl",
            "laminat": "laminate",
            "laminated": "laminate",
            "laminate": "laminate",
            "wood": "wood flooring",
            "wooden": "wood flooring",
            "hardwood": "wood flooring",
            "timber": "wood flooring",
        }
        
        return typo_map.get(product_type, product_type)
    
    def _get_color_variations(self, color: str) -> List[str]:
        """Get color variations and synonyms, including common typos"""
        color = color.lower().strip()
        color_map = {
            "grey": ["grey", "gray"],
            "gray": ["grey", "gray"],
            "beige": ["beige", "tan", "cream", "biege"],
            "brown": ["brown", "chocolate", "espresso", "bronw"],
            "white": ["white", "ivory", "off-white", "wite"],
            "black": ["black", "ebony", "charcoal", "blak"],
            "red": ["red", "burgundy", "crimson"],
            "blue": ["blue", "navy", "azure", "blu"],
            "green": ["green", "olive", "sage"],
            "oak": ["oak", "light oak", "natural oak"],
            "walnut": ["walnut", "dark walnut"],
            "yellow": ["yellow", "gold", "golden"],
            "orange": ["orange", "terracotta"],
            "purple": ["purple", "violet", "lavender"],
        }
        return color_map.get(color, [color])
    
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
        
        # Get image URL
        image_url = None
        if product.primary_image:
            image_url = product.primary_image.url if hasattr(product.primary_image, 'url') else str(product.primary_image)
        
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
            image_url=image_url,
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
