session = await client.create_session({
        "model": "gpt-4.1",
        "system_message": {
            "mode": "replace",
            "content": "You are a sales assistant helping customers find products. You have access to a product search tool that can search for products based on name, color, and price range. Use the tool to find products for customers based on their queries."
        }
    })