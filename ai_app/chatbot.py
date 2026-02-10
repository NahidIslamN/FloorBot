"""
FloorBot AI Chatbot Engine - Core conversational AI using OpenAI GPT-4
"""
import json
from typing import Optional, Dict, List, Any
from openai import OpenAI
from ai_app.config import AIConfig
from ai_app.schemas import ChatSession, MessageRole
from ai_app.session_manager import SessionManager
from ai_app.product_service import DjangoProductService
from ai_app.order_calculator import OrderCalculator


class FloorBotAI:
    """Main AI chatbot engine for FloorBot"""
    
    def __init__(self):
        """Initialize FloorBot AI"""
        self.client = OpenAI(api_key=AIConfig.OPENAI_API_KEY)
        self.model = AIConfig.OPENAI_MODEL
        self.temperature = AIConfig.OPENAI_TEMPERATURE
        self.max_tokens = AIConfig.OPENAI_MAX_TOKENS
        
        self.session_manager = SessionManager()
        self.product_service = DjangoProductService()
        self.order_calculator = OrderCalculator(self.product_service)
        
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict]:
        """Define function calling tools for OpenAI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for flooring products based on customer requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_type": {
                                "type": "string",
                                "description": "Type of flooring (carpets, vinyl, laminate, wood flooring)"
                            },
                            "color": {
                                "type": "string",
                                "description": "Preferred color"
                            },
                            "material": {
                                "type": "string",
                                "description": "Material type"
                            },
                            "max_price": {
                                "type": "number",
                                "description": "Maximum price per unit"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_area",
                    "description": "Calculate room area from dimensions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "width": {
                                "type": "number",
                                "description": "Room width in meters"
                            },
                            "length": {
                                "type": "number",
                                "description": "Room length in meters"
                            }
                        },
                        "required": ["width", "length"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_quantity",
                    "description": "Calculate quantity needed for a product to cover an area",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "Product ID"
                            },
                            "area": {
                                "type": "number",
                                "description": "Area to cover in square meters"
                            }
                        },
                        "required": ["product_id", "area"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_order_summary",
                    "description": "Create order summary with pricing for selected products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "description": "List of items to order",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "product_id": {"type": "string"},
                                        "quantity": {"type": "number"}
                                    },
                                    "required": ["product_id", "quantity"]
                                }
                            }
                        },
                        "required": ["items"]
                    }
                }
            }
        ]
    
    def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Process a chat message
        
        Args:
            session_id: Session ID
            message: User message
            
        Returns:
            Response dictionary with AI reply
        """
        session = self.session_manager.get_session(session_id)
        
        if not session:
            return {
                "session_id": session_id,
                "response": "Session not found. Please create a new session.",
                "success": False
            }
        
        session.add_message(MessageRole.USER, message)
        
        try:
            messages = session.get_openai_messages(limit=AIConfig.MAX_CONVERSATION_HISTORY)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            assistant_message = response.choices[0].message
            
            if assistant_message.tool_calls:
                function_responses = []
                
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    function_response = self._execute_function(function_name, function_args)
                    
                    function_responses.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_response)
                    })
                
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                messages.extend(function_responses)
                
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                final_content = second_response.choices[0].message.content
            else:
                final_content = assistant_message.content
            
            session.add_message(MessageRole.ASSISTANT, final_content)
            self.session_manager.update_session(session)
            
            return {
                "session_id": session_id,
                "response": final_content,
                "success": True
            }
        
        except Exception as e:
            return {
                "session_id": session_id,
                "response": f"I encountered an error: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _execute_function(self, function_name: str, arguments: Dict) -> Dict:
        """Execute a function call from GPT"""
        
        if function_name == "search_products":
            products = self.product_service.search_products(
                product_type=arguments.get("product_type"),
                color=arguments.get("color"),
                material=arguments.get("material"),
                max_price=arguments.get("max_price")
            )
            
            return {
                "products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "category": p.category,
                        "price": p.sale_price if p.sale_price > 0 else p.price_per_unit,
                        "unit": p.unit,
                        "coverage": p.coverage_per_unit,
                        "discount": p.discount_percentage,
                        "stock": p.stock_quantity,
                        "description": p.description[:200]
                    }
                    for p in products
                ],
                "count": len(products)
            }
        
        elif function_name == "calculate_area":
            width = arguments["width"]
            length = arguments["length"]
            area = self.order_calculator.calculate_area(width, length)
            return {
                "width": width,
                "length": length,
                "area": area,
                "unit": "square meters"
            }
        
        elif function_name == "calculate_quantity":
            product_id = arguments["product_id"]
            area = arguments["area"]
            
            product = self.product_service.get_product_by_id(product_id)
            if not product:
                return {"error": "Product not found"}
            
            quantity = self.order_calculator.calculate_quantity_needed(area, product)
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "area": area,
                "quantity": quantity,
                "unit": product.unit,
                "coverage_per_unit": product.coverage_per_unit
            }
        
        elif function_name == "create_order_summary":
            items_data = arguments["items"]
            order_items = []
            
            for item_data in items_data:
                order_item = self.order_calculator.calculate_order_item(
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"]
                )
                if order_item:
                    order_items.append(order_item)
            
            if not order_items:
                return {"error": "No valid items found"}
            
            summary = self.order_calculator.create_order_summary(
                items=order_items,
                tax_rate=0.1,
                delivery_fee=0.0
            )
            
            return summary.to_dict()
        
        return {"error": f"Unknown function: {function_name}"}
