"""
Data schemas for AI chatbot
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class MessageRole(str, Enum):
    """Message roles in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass
class ConversationMessage:
    """Single message in a conversation"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Chat session with conversation history and context"""
    session_id: str
    user_id: Optional[str] = None
    messages: List[ConversationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict] = None):
        """Add a message to the session"""
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history as list of dicts"""
        messages = self.messages[-limit:] if limit else self.messages
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in messages
        ]
    
    def get_openai_messages(self, limit: Optional[int] = None) -> List[Dict]:
        """Get messages formatted for OpenAI API"""
        messages = self.messages[-limit:] if limit else self.messages
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]


@dataclass
class ProductInfo:
    """Product information adapted from Django model"""
    id: str
    name: str
    category: str
    color: str
    material: str
    price_per_unit: float
    sale_price: float
    unit: str
    coverage_per_unit: float
    stock_quantity: int
    discount_percentage: float
    description: str
    specifications: Dict[str, Any]
    image_url: Optional[str] = None
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get formatted product info for display"""
        final_price = self.sale_price if self.sale_price > 0 else self.price_per_unit
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "color": self.color,
            "material": self.material,
            "price": f"${final_price:.2f}",
            "unit": self.unit,
            "coverage": f"{self.coverage_per_unit} m²" if self.unit == "box" else "1 m²",
            "discount": f"{self.discount_percentage}%" if self.discount_percentage > 0 else "No discount",
            "stock": f"{self.stock_quantity} in stock",
            "description": self.description,
            "image_url": self.image_url
        }


@dataclass
class OrderItem:
    """Individual item in an order"""
    product: ProductInfo
    quantity: float
    area_covered: float
    unit_price: float
    subtotal: float
    discount_amount: float
    total: float


@dataclass
class OrderSummary:
    """Complete order summary"""
    items: List[OrderItem]
    subtotal: float
    total_discount: float
    tax: float
    delivery_fee: float
    grand_total: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "items": [
                {
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit": item.product.unit,
                    "area_covered": f"{item.area_covered} m²",
                    "unit_price": f"${item.unit_price:.2f}",
                    "subtotal": f"${item.subtotal:.2f}",
                    "discount": f"${item.discount_amount:.2f}",
                    "total": f"${item.total:.2f}"
                }
                for item in self.items
            ],
            "summary": {
                "subtotal": f"${self.subtotal:.2f}",
                "discount": f"${self.total_discount:.2f}",
                "tax": f"${self.tax:.2f}",
                "delivery": f"${self.delivery_fee:.2f}",
                "grand_total": f"${self.grand_total:.2f}"
            }
        }
