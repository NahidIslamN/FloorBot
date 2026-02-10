# AI App - FloorBot AI Assistant

## Overview

This app provides AI-powered chatbot functionality for FloorBot, helping customers find and order flooring products through natural language conversations.

## Features

- Text chat with GPT-4
- Voice input with Whisper transcription
- Product search and recommendations
- Area and quantity calculations
- Order summary generation
- Session management with conversation history

## Structure

```
ai_app/
├── config.py              # AI configuration
├── schemas.py             # Data models
├── session_manager.py     # Session handling
├── product_service.py     # Product search
├── order_calculator.py    # Calculations
├── speech_service.py      # Voice transcription
├── chatbot.py            # Core AI engine
├── api.py                # Simple API interface
├── views.py              # Django REST views
├── serializers.py        # API serializers
├── urls.py               # URL routing
└── tests.py              # Tests
```

## Quick Start

1. Install dependencies: `pip install openai>=1.10.0`
2. Set `OPENAI_API_KEY` in environment
3. Configure cache backend in settings.py
4. Include `path('api/ai/', include('ai_app.urls'))` in main urls.py

## API Usage

See `AI_INTEGRATION_GUIDE.md` in project root for complete integration guide.

## Testing

```python
python manage.py test ai_app
```

## Dependencies

- openai>=1.10.0
- Django cache framework (Redis/Memcached recommended)
