# API smoke checks

```bash
curl -sS "$API_URL/public/orders/<order_id>" | jq .
```

Expected: `items` array contains real order items with fields `id`, `title`, `price`, `quantity`.
