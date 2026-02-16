"""
Example Usage: Testing AI Product Search Feature

This demonstrates how the AI chatbot now returns products along with text responses.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api/ai"


def test_basic_product_search():
    """Test basic product search"""
    print("=" * 60)
    print("Test 1: Basic Product Search")
    print("=" * 60)
    
    # Create a new session
    session_response = requests.post(f"{API_BASE_URL}/session/create/")
    session_data = session_response.json()
    session_id = session_data['session_id']
    print(f"Created session: {session_id}\n")
    
    # Ask for carpets
    chat_data = {
        "message": "I need carpets",
        "session_id": session_id
    }
    
    response = requests.post(f"{API_BASE_URL}/chat/", json=chat_data)
    result = response.json()
    
    print(f"User: {chat_data['message']}")
    print(f"\nAI Response: {result['response']}")
    
    if result.get('products'):
        print(f"\nProducts Found: {result['product_count']}")
        print("\nTop 3 Products:")
        for i, product in enumerate(result['products'][:3], 1):
            print(f"\n{i}. {product['name']}")
            print(f"   Category: {product['category']}")
            print(f"   Price: ${product['sale_price']}/{product['unit']}")
            print(f"   Color: {product['color']}")
            print(f"   Stock: {product['stock']}")
            if product['discount'] > 0:
                print(f"   Discount: {product['discount']}%")
    
    return session_id


def test_iterative_filtering(session_id):
    """Test iterative filtering with follow-up questions"""
    print("\n" + "=" * 60)
    print("Test 2: Iterative Filtering")
    print("=" * 60)
    
    # Ask for grey color
    chat_data = {
        "message": "Grey ones",
        "session_id": session_id
    }
    
    response = requests.post(f"{API_BASE_URL}/chat/", json=chat_data)
    result = response.json()
    
    print(f"\nUser: {chat_data['message']}")
    print(f"\nAI Response: {result['response']}")
    
    if result.get('products'):
        print(f"\nProducts Found (Grey Carpets): {result['product_count']}")
        for i, product in enumerate(result['products'][:3], 1):
            print(f"{i}. {product['name']} - ${product['sale_price']} - {product['color']}")
    
    # Ask for modern style
    chat_data = {
        "message": "Modern style",
        "session_id": session_id
    }
    
    response = requests.post(f"{API_BASE_URL}/chat/", json=chat_data)
    result = response.json()
    
    print(f"\n\nUser: {chat_data['message']}")
    print(f"\nAI Response: {result['response']}")
    
    if result.get('products'):
        print(f"\nProducts Found (Modern Grey Carpets): {result['product_count']}")


def test_specific_search():
    """Test specific product search with multiple criteria"""
    print("\n" + "=" * 60)
    print("Test 3: Specific Search with Multiple Criteria")
    print("=" * 60)
    
    # Create new session
    session_response = requests.post(f"{API_BASE_URL}/session/create/")
    session_id = session_response.json()['session_id']
    
    # Search with specific requirements
    chat_data = {
        "message": "I'm looking for beige vinyl flooring under $45 per square meter",
        "session_id": session_id
    }
    
    response = requests.post(f"{API_BASE_URL}/chat/", json=chat_data)
    result = response.json()
    
    print(f"User: {chat_data['message']}")
    print(f"\nAI Response: {result['response']}")
    
    if result.get('products'):
        print(f"\nProducts Found: {result['product_count']}")
        for i, product in enumerate(result['products'], 1):
            print(f"\n{i}. {product['name']}")
            print(f"   Price: ${product['sale_price']}/{product['unit']}")
            print(f"   Color: {product['color']}")


def test_voice_simulation():
    """Test voice chat (simulated with text)"""
    print("\n" + "=" * 60)
    print("Test 4: Voice Chat Simulation")
    print("=" * 60)
    print("Note: This would normally use base64 encoded audio")
    print("For testing, we'll use the text endpoint\n")
    
    # Create new session
    session_response = requests.post(f"{API_BASE_URL}/session/create/")
    session_id = session_response.json()['session_id']
    
    # Simulate voice: "Show me wood flooring"
    chat_data = {
        "message": "Show me wood flooring",
        "session_id": session_id
    }
    
    response = requests.post(f"{API_BASE_URL}/chat/", json=chat_data)
    result = response.json()
    
    print(f"Voice Input (transcribed): {chat_data['message']}")
    print(f"\nAI Response: {result['response']}")
    
    if result.get('products'):
        print(f"\nProducts Found: {result['product_count']}")
        print("\nSample Products:")
        for i, product in enumerate(result['products'][:3], 1):
            print(f"{i}. {product['name']} - ${product['sale_price']}")


def test_conversation_flow():
    """Test complete conversation flow"""
    print("\n" + "=" * 60)
    print("Test 5: Complete Conversation Flow")
    print("=" * 60)
    
    # Create new session
    session_response = requests.post(f"{API_BASE_URL}/session/create/")
    session_id = session_response.json()['session_id']
    
    conversation = [
        "Hi, I need flooring for my living room",
        "Laminate would be good",
        "Show me oak colored options",
        "What about under $50?",
    ]
    
    for message in conversation:
        chat_data = {
            "message": message,
            "session_id": session_id
        }
        
        response = requests.post(f"{API_BASE_URL}/chat/", json=chat_data)
        result = response.json()
        
        print(f"\nUser: {message}")
        print(f"AI: {result['response']}")
        
        if result.get('products'):
            print(f"   [Showing {result['product_count']} products]")


def display_response_structure():
    """Show the structure of API response"""
    print("\n" + "=" * 60)
    print("API Response Structure Example")
    print("=" * 60)
    
    example_response = {
        "session_id": "abc-123-def",
        "response": "I found several carpet options for you! What color would you like?",
        "success": True,
        "products": [
            {
                "id": "PROD-001",
                "name": "Luxury Grey Carpet",
                "category": "carpets",
                "price": 45.99,
                "sale_price": 39.99,
                "unit": "m2",
                "coverage": 1.0,
                "discount": 13.05,
                "stock": 150,
                "description": "Premium quality carpet...",
                "color": "Grey",
                "material": "Wool blend",
                "image_url": "/media/products/carpet-001.jpg"
            }
        ],
        "product_count": 8
    }
    
    print(json.dumps(example_response, indent=2))


if __name__ == "__main__":
    print("\n🤖 FloorBot AI - Product Search Feature Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        session_id = test_basic_product_search()
        test_iterative_filtering(session_id)
        test_specific_search()
        test_voice_simulation()
        test_conversation_flow()
        display_response_structure()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Make sure the Django server is running on http://localhost:8000")
        print("Run: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
