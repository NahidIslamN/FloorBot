# Webhook Debugging Guide

## Problem Summary

You're seeing:
```
2026-04-13 05:26:53,821 INFO  Stripe API response... 200
10.10.12.15:37160 - - [13/Apr/2026:05:26:53] "POST /api/v1/users/orders-create/" 200 382
success
2026-04-13 05:27:43,351 WARNING  Webhook skipped: missing user_id in Stripe metadata
172.18.0.1:48024 - - [13/Apr/2026:05:27:43] "POST /api/v2/stripe-webhock-after-payment-successs/" 200 15
```

**What this means:**
- ✅ Order creation endpoint succeeded (200, "success" printed)
- ✅ Webhook endpoint was called (200 OK)
- ❌ BUT the webhook couldn't process the order (missing user_id)

## Root Cause

The webhook is receiving **test payment events** that don't have the same metadata structure as the actual payment intents created by the app.

### Payment Intent Creation Flow

When you call `/api/v1/users/orders-create/` or `/api/v2/create-orders/`:

```python
metadata={
    "user_id": str(user.id),              # ✅ Set here
    "product_id": str(product.id),        # ✅ Set here
    "qty": str(qty),                      # ✅ Set here
    "items": json.dumps([...]),           # ✅ Set here
    "source": "flor_bot_orders",          # ✅ App marker
    "country_or_region": ...,             # ✅ Address
    ...
}
```

### Webhook Processing Flow

When the webhook is triggered:

```python
# 1. Event filter - checks if this is an app-generated order
if not _is_flor_bot_order_intent(metadata):
    logger.info("Webhook ignored: non-app payment intent")
    return HTTP 200  # ← Test events fail here

# 2. Parse items
items_data = _parse_order_items_from_metadata(metadata)
# ← May fail if metadata missing "items" or "products"

# 3. Resolve user
user_id = _resolve_user_id_from_metadata(metadata)
if user_id is None:
    logger.warning("❌ Webhook skipped: missing user_id")
    # ← This is where your logs show the failure
    return None
```

## Why Test Events Fail

When you trigger a test webhook from Stripe's dashboard or CLI:

```json
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_test123",
      "amount_received": 5000,
      "metadata": {}  // ← Empty! No source, user_id, products, etc.
    }
  }
}
```

The metadata is empty because:
- Stripe test events don't know about your app's custom metadata
- Only payment intents created by **your app** (via the `/orders-create/` endpoints) have the full metadata

## New Enhanced Logging

We've added detailed logging to trace every step:

```
✅ Webhook event received - payment_intent_id: pi_xxx
📦 Payment metadata: {...}
🔍 Source check: source=flor_bot_orders, is_flor_bot=True
💰 Processing order: amount=50.00, payment_intent=pi_xxx
🔄 Starting order creation from metadata...
📋 Metadata received: {...}
✅ Order successfully created: order_id=5, user_id=3, items=2, total=50.00
✨ Order V2 created successfully: order_id=5
```

## Testing the Complete Flow

### Step 1: Create a Real Order

```bash
curl -X POST http://localhost:8000/api/v1/users/orders-create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "product_id": 1,
    "qty": 1,
    "country_or_region": "UK",
    "address_line_i": "123 Main St",
    "address_line_ii": "",
    "suburb": "London",
    "city": "London",
    "postal_code": "SW1A 1AA",
    "state": "England"
  }'
```

**Expected logs:**
```
2026-04-13 05:26:53,821 INFO  Stripe API response... 200
10.10.12.15:37160 - - [13/Apr/2026:05:26:53] "POST /api/v1/users/orders-create/" 200 382
```

This returns:
```json
{
  "success": true,
  "payment": {
    "payment_intent_id": "pi_abc123",
    "client_secret": "pi_abc123_secret_xyz",
    "amount": 50.00
  }
}
```

### Step 2: Simulate Stripe Webhook

Use the `payment_intent_id` from the response above in your webhook test.

**If using Stripe CLI:**
```bash
stripe trigger payment_intent.succeeded \
  --override metadata.user_id=3 \
  --override metadata.source=flor_bot_orders \
  --override metadata.items='[{"product_id":1,"qty":1}]'
```

**If using Stripe Dashboard:**
1. Go to Developers → Webhooks
2. Find your endpoint
3. Click "Send test event" 
4. Select "payment_intent.succeeded"
5. BUT the test event will have empty metadata → order will be ignored ✓ (This is correct behavior)

### Step 3: Real Webhook Test (Recommended)

Actually complete the payment flow:

1. Frontend completes payment with Stripe (enters card, etc.)
2. Stripe automatically triggers `payment_intent.succeeded` webhook
3. Your endpoint receives the real metadata with user_id, products, etc.
4. Order is created automatically

## Logs to Watch For

### ✅ Success Case
```
✅ Webhook event received - payment_intent_id: pi_1A2B3C4D5E
📦 Payment metadata: {'user_id': '3', 'source': 'flor_bot_orders', ...}
🔍 Source check: source=flor_bot_orders, is_flor_bot=True
💰 Processing order: amount=50.00, payment_intent=pi_1A2B3C4D5E
🔄 Starting order creation from metadata...
✅ Order successfully created: order_id=42, user_id=3, items=2, total=50.00
✨ Order created successfully: order_id=42
```

### ⏭️ Duplicate Case (Idempotent)
```
✅ Webhook event received...
⏭️ Order already exists for payment_intent=pi_xxx, returning existing order
```
*This is fine - Stripe retries failed deliveries, we ignore duplicates*

### ❌ Non-App Event Case
```
✅ Webhook event received...
📦 Payment metadata: {}
🔍 Source check: source=None, is_flor_bot=False
Webhook ignored: non-app payment intent (source=None)
```
*This is expected for test events - they're safely ignored*

### ❌ Missing User Case
```
✅ Webhook event received...
📦 Payment metadata: {'items': [...]}
🔍 Source check: source=flor_bot_orders, is_flor_bot=True
💰 Processing order...
📋 Metadata received: {'items': [...]}
❌ Webhook skipped: missing user_id in Stripe metadata. Keys: ['items']
```
*This means the payment intent was created without user_id - check your order creation endpoint*

## Checklist for Production

- [ ] Both order creation endpoints (`User_Ordedrs.post()` and `CreateOrdersV2.post()`) include `"source": "flor_bot_orders"` in metadata
- [ ] All metadata values are strings: `str(user.id)`, `str(qty)`, etc.
- [ ] Webhook endpoint has authentication disabled (`authentication_classes = []`)
- [ ] Webhook endpoint accepts both `.json` and regular data
- [ ] Stripe webhook signature is verified
- [ ] OrderTable has `tracking_no` set to `payment_intent_id` for idempotency
- [ ] Orders created via webhook are NOT created twice on retry
- [ ] Test events from Stripe dashboard safely return 200 without creating duplicate orders
- [ ] Production payment completions automatically create orders

## Code Changes Made

1. **Metadata**: All values now strings (`str(user.id)`)
2. **Source marker**: `"source": "flor_bot_orders"` added to all payment intents
3. **Event filtering**: Webhook ignores non-app events (test events, external charges, etc.)
4. **Detailed logging**: Each step now logged with emoji prefixes for easy scanning
5. **Idempotency**: `tracking_no=payment_intent_id` prevents duplicate orders

## Files Modified

- `/salseApp/views.py`: Enhanced logging, source marker check, better error messages
