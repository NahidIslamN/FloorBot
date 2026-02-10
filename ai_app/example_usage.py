"""
Example usage of FloorBot AI

Run this file to test the AI integration:
python manage.py shell < ai_app/example_usage.py
"""

def test_ai_chat():
    """Test AI chat functionality"""
    from ai_app.api import FloorBotAPI
    
    print("FloorBot AI Test")
    print("=" * 50)
    
    api = FloorBotAPI()
    
    print("\n1. Creating session...")
    session = api.create_session()
    print(f"Session ID: {session.session_id}")
    
    print("\n2. Sending message: 'I need grey carpet for a 5x4 meter room'")
    response = api.send_text_message(
        session.session_id,
        "I need grey carpet for a 5x4 meter room"
    )
    print(f"AI Response: {response['response']}")
    
    print("\n3. Getting conversation history...")
    history = api.get_history(session.session_id)
    print(f"Messages in history: {len(history)}")
    
    print("\n4. Deleting session...")
    api.delete_session(session.session_id)
    print("Session deleted")
    
    print("\nTest complete!")


if __name__ == "__main__":
    test_ai_chat()
