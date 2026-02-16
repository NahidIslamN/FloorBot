# AI Product Search Feature

## Overview
The AI chatbot now intelligently searches and displays products based on natural language queries. When users ask about products through chat or voice, the AI automatically:

1. **Analyzes keywords** from the user's message
2. **Searches products** from the database
3. **Returns both**:
   - Conversational text response
   - Actual product data (with images, prices, descriptions)
4. **Supports iterative filtering** through follow-up questions

## How It Works

### Example Conversation Flow

#### Example 1: Basic Product Search
```
User: "I need some carpets"

AI Response:
- Text: "I found several carpet options for you! They're displayed above. To help you narrow it down, what color are you looking for? We have grey, beige, brown, and more options available."
- Products: [List of 10 carpet products with images, prices, descriptions]

User: "Grey ones"

AI Response:
- Text: "Great choice! I've filtered the results to show grey carpets. You can see them above. Are you looking for a specific style or material?"
- Products: [List of grey carpets only]

User: "Modern style"

AI Response:
- Text: "Perfect! Here are our modern grey carpets. These would look great in contemporary spaces."
- Products: [List of modern grey carpets]
```

#### Example 2: Voice Search
```
User: (Voice) "Show me vinyl flooring"

AI Response:
- Transcribed: "Show me vinyl flooring"
- Text: "I've found several vinyl flooring options for you! Check them out above. What color scheme are you looking for?"
- Products: [List of vinyl flooring products]

User: (Voice) "Beige or cream"

AI Response:
- Transcribed: "Beige or cream"
- Text: "Here are our beige and cream vinyl options. They're very popular for living rooms and bedrooms!"
- Products: [List of beige/cream vinyl products]
```

#### Example 3: Specific Requirements
```
User: "I'm looking for oak wood flooring under $50 per square meter"

AI Response:
- Text: "I've found oak wood flooring within your budget! Here are the options under $50 per square meter."
- Products: [List of oak flooring under $50]
```

## API Response Format

### Text Chat Request
```json
POST /api/ai/chat/
{
  "message": "I need carpets",
  "session_id": "abc-123-def"
}
```

### Response with Products
```json
{
  "session_id": "abc-123-def",
  "response": "I found several carpet options for you! They're displayed above. What color are you looking for?",
  "success": true,
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
      "description": "Premium quality carpet with soft texture...",
      "color": "Grey",
      "material": "Wool blend",
      "image_url": "/media/products/carpet-grey-001.jpg"
    },
    // ... more products
  ],
  "product_count": 8
}
```

### Voice Chat Request
```json
POST /api/ai/voice-chat/
{
  "audio_data": "base64_encoded_audio...",
  "audio_format": "wav",
  "session_id": "abc-123-def",
  "language": "en"
}
```

### Response with Transcription and Products
```json
{
  "session_id": "abc-123-def",
  "response": "I've found vinyl flooring options for you! What color would you prefer?",
  "transcribed_text": "Show me vinyl flooring",
  "success": true,
  "products": [...],
  "product_count": 10
}
```

## Search Capabilities

### 1. Product Type Recognition
The AI recognizes various ways of asking for products:
- "I need carpets" → searches carpets
- "Show me vinyl" → searches vinyl flooring
- "Looking for wood floors" → searches wood flooring
- "What laminate do you have?" → searches laminate

### 2. Color Extraction
Automatically detects color preferences:
- "Grey carpets" → filters by grey color
- "I want beige" → filters by beige
- "Show me oak flooring" → filters by oak color/material

### 3. Material Matching
Recognizes material types:
- "Wool carpets" → filters by wool material
- "Engineered wood" → filters by engineered material

### 4. Pattern/Style Recognition
Understands style preferences:
- "Modern carpets" → filters by modern pattern
- "Traditional vinyl" → filters by traditional style
- "Rustic wood" → filters by rustic pattern

### 5. Price Filtering
Extracts price requirements:
- "Under $50" → sets max_price to 50
- "Budget-friendly options" → triggers price filtering

### 6. Follow-up Filtering
Maintains context for iterative refinement:
```
User: "Carpets" → Shows all carpets
User: "Grey" → Shows grey carpets (remembers it's carpets)
User: "Modern" → Shows modern grey carpets (remembers both filters)
```

## Frontend Integration

### Display Products
When you receive a response with `products` array:

```javascript
// React example
function ChatMessage({ message }) {
  return (
    <>
      {/* Text response */}
      <div className="ai-message">{message.response}</div>
      
      {/* Product grid (if products exist) */}
      {message.products && message.products.length > 0 && (
        <div className="product-grid">
          {message.products.map(product => (
            <ProductCard 
              key={product.id}
              product={product}
            />
          ))}
        </div>
      )}
    </>
  );
}

function ProductCard({ product }) {
  const displayPrice = product.sale_price || product.price;
  
  return (
    <div className="product-card">
      <img src={product.image_url} alt={product.name} />
      <h3>{product.name}</h3>
      <p className="category">{product.category}</p>
      <p className="price">
        ${displayPrice} / {product.unit}
        {product.discount > 0 && (
          <span className="discount">-{product.discount}%</span>
        )}
      </p>
      <p className="description">{product.description}</p>
      <div className="details">
        <span>Color: {product.color}</span>
        <span>Stock: {product.stock}</span>
      </div>
    </div>
  );
}
```

## Session Context Tracking

The AI stores search context in the session:

```python
session.context = {
  "last_search_filters": {
    "product_type": "carpets",
    "color": "grey",
    "material": None,
    "pattern": "modern",
    "max_price": None,
    "keyword": None
  },
  "last_products": ["PROD-001", "PROD-002", ...]
}
```

This allows the AI to:
- Remember what type of products the user is interested in
- Apply incremental filters on follow-up questions
- Provide context-aware responses

## Enhanced Features

### 1. Color Variations
The system recognizes color synonyms:
- "Grey" also matches "Gray"
- "Beige" also matches "Tan", "Cream"
- "Brown" also matches "Chocolate", "Espresso"

### 2. Category Keywords
Expanded keyword matching for product types:
- Carpets: "carpet", "carpets", "rug", "rugs"
- Vinyl: "vinyl", "lvt", "luxury vinyl", "vinyl tile", "vinyl plank"
- Wood: "wood", "hardwood", "engineered wood", "timber", "wooden", "oak", "walnut"

### 3. Smart Product Limit
Returns top 10 most relevant products to avoid overwhelming users

### 4. In-Stock Only
Only shows products with available stock

## Testing the Feature

### Test with cURL

```bash
# Text chat
curl -X POST http://localhost:8000/api/ai/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need grey carpets",
    "session_id": null
  }'

# Voice chat (base64 audio)
curl -X POST http://localhost:8000/api/ai/voice-chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_encoded_audio_here",
    "audio_format": "wav",
    "session_id": null,
    "language": "en"
  }'
```

### Test Scenarios

1. **Basic Search**: "Show me carpets"
2. **With Color**: "I need grey vinyl flooring"
3. **With Material**: "Looking for wool carpets"
4. **With Price**: "Carpets under $40 per square meter"
5. **Follow-up Filter**: 
   - "Show me carpets"
   - "Grey ones"
   - "Modern style"
6. **Voice Search**: Say "I want wood flooring"

## Implementation Files Modified

1. **serializers.py**: Added `ProductSerializer` and updated `ChatResponseSerializer`
2. **chatbot.py**: 
   - Modified `chat()` to track and return products
   - Updated `_execute_function()` to store context
   - Enhanced `search_products` tool definition
3. **product_service.py**: 
   - Added color variation support
   - Enhanced keyword matching
   - Added pattern and keyword parameters
4. **schemas.py**: Added `image_url` to `ProductInfo`
5. **config.py**: Updated system prompt with product search behavior

## Benefits

1. ✅ **Better User Experience**: Products shown immediately when mentioned
2. ✅ **Natural Conversation**: Users can ask in plain language
3. ✅ **Visual Discovery**: Images help users decide quickly
4. ✅ **Iterative Refinement**: Easy to narrow down options
5. ✅ **Works with Voice**: Same experience for voice queries
6. ✅ **Context Aware**: Remembers previous filters
7. ✅ **Structured Data**: Frontend gets clean product data

## Next Steps

Consider adding:
- Product comparison feature
- "Add to cart" from AI chat
- Image-based product search
- Recommendation engine based on user preferences
- Product availability by location
- Installation cost estimation
