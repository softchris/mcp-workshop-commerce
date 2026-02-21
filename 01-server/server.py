# server.py
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, AsyncGenerator
from mcp.types import (
    LoggingMessageNotificationParams,
    TextContent
)

# Create an MCP server
mcp = FastMCP("Streamable DEMO")

faq = {
    "What is your return policy?": "Our return policy allows customers to return products within 30 days of purchase for a full refund, provided the items are in their original condition and packaging.",
    "Do you offer international shipping?": "Yes, we offer international shipping to select countries. Shipping fees and delivery times vary based on the destination.",
    "How can I track my order?": "Once your order has been shipped, you will receive a tracking number via email. You can use this number on our website to track the status of your delivery.",
    "What payment methods do you accept?": "We accept various payment methods including credit/debit cards, PayPal, and Apple Pay.",
    "How do I contact customer support?": "You can contact our customer support team via email at support@example.com."
}

products = [
        {"name": "Cotton T-Shirt", "price": 19.99, "color": "red"}, 
        {"name": "Denim Jeans", "price": 49.99, "color": "blue"},  
        {"name": "Wool Sweater", "price": 79.99, "color": "navy"},  
        {"name": "Summer Dress", "price": 39.99, "color": "floral"},
        {"name": "Leather Jacket", "price": 199.99, "color": "black"},
        {"name": "Silk Blouse", "price": 89.99, "color": "white"},
        {"name": "Cargo Shorts", "price": 29.99, "color": "khaki"},
        {"name": "Winter Coat", "price": 149.99, "color": "gray"},
        {"name": "Athletic Hoodie", "price": 59.99, "color": "green"},
        {"name": "Formal Blazer", "price": 129.99, "color": "charcoal"}      
    ]

@mcp.tool(description="Answer frequently asked questions about our store policies and services")
async def faq_tool(question: str, ctx: Context) -> str:
    # First try exact match for backward compatibility
    if question in faq:
        return faq[question]
    
    # Convert input to lowercase for case-insensitive matching
    question_lower = question.lower().strip()
    
    # Try to find questions that contain the user's input as a substring
    for faq_question, faq_answer in faq.items():
        if question_lower in faq_question.lower():
            return faq_answer
    
    # Try to find if user's input contains keywords from FAQ questions
    question_words = set(question_lower.split())
    best_match = None
    max_word_matches = 0
    
    for faq_question, faq_answer in faq.items():
        faq_words = set(faq_question.lower().split())
        # Remove common words that aren't very meaningful
        faq_words = {word for word in faq_words if word not in {'is', 'your', 'do', 'you', 'what', 'how', 'can', 'i', 'the', 'a', 'an', 'to', 'for'}}
        
        # Count matching words
        word_matches = len(question_words.intersection(faq_words))
        if word_matches > 0 and word_matches > max_word_matches:
            max_word_matches = word_matches
            best_match = faq_answer
    
    return best_match if best_match else "Sorry, I don't have an answer to that question."

def _matches_search_term(term: str, product: Dict[str, Any]) -> bool:
    """
    Enhanced matching that handles plurals, partial matches, and common variations.
    """
    term_lower = term.lower().strip()
    name_lower = product["name"].lower()
    color_lower = product["color"].lower()
    
    # Direct substring match
    if term_lower in name_lower or term_lower in color_lower:
        return True
    
    # Handle common plural/singular forms
    if term_lower.endswith('s') and len(term_lower) > 3:
        singular = term_lower[:-1]
        if singular in name_lower or singular in color_lower:
            return True
    
    # Handle adding 's' for plural search
    plural = term_lower + 's'
    if plural in name_lower or plural in color_lower:
        return True
    
    # Handle 'ies' to 'y' conversion (e.g., accessories -> accessory)
    if term_lower.endswith('ies') and len(term_lower) > 4:
        singular_y = term_lower[:-3] + 'y'
        if singular_y in name_lower or singular_y in color_lower:
            return True
    
    # Handle 'y' to 'ies' conversion
    if term_lower.endswith('y') and len(term_lower) > 2:
        plural_ies = term_lower[:-1] + 'ies'
        if plural_ies in name_lower or plural_ies in color_lower:
            return True
    
    # Word boundary matching - check if term matches any complete word
    import re
    pattern = r'\b' + re.escape(term_lower) + r'\b'
    if re.search(pattern, name_lower) or re.search(pattern, color_lower):
        return True
    
    return False

@mcp.tool(description="Search for a product by name, price range, or color")
async def search_product(
    query: str = "",
    name: str = "",
    color: str = "", 
    min_price: float = 0,
    max_price: float = 999999,
    ctx: Context = None
) -> List[Dict[str, Any]]: 
    global products
    
    filtered_products = products.copy()
    
    # Apply price filters
    if min_price > 0:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    if max_price < 999999:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    # Apply name filter
    if name.strip():
        filtered_products = [p for p in filtered_products if _matches_search_term(name, p)]
    
    # Apply color filter  
    if color.strip():
        filtered_products = [p for p in filtered_products if color.lower() in p["color"].lower()]
    
    # Fallback to legacy query parsing for backward compatibility
    if query.strip() and not any([name, color, min_price > 0, max_price < 999999]):
        import re
        query_lower = query.lower()
        
        # Extract price constraints
        extracted_max_price = None
        extracted_min_price = None
        
        if "under" in query_lower or "below" in query_lower:
            price_match = re.search(r'(?:under|below)\s*(\d+\.?\d*)', query_lower)
            if price_match:
                extracted_max_price = float(price_match.group(1))
        
        if "over" in query_lower or "above" in query_lower:
            price_match = re.search(r'(?:over|above)\s*(\d+\.?\d*)', query_lower)
            if price_match:
                extracted_min_price = float(price_match.group(1))
        
        if "between" in query_lower:
            price_matches = re.findall(r'(\d+\.?\d*)', query_lower)
            if len(price_matches) >= 2:
                extracted_min_price = float(price_matches[0])
                extracted_max_price = float(price_matches[1])
        
        # Apply extracted price filters
        if extracted_max_price is not None:
            filtered_products = [p for p in filtered_products if p["price"] < extracted_max_price]
        if extracted_min_price is not None:
            filtered_products = [p for p in filtered_products if p["price"] > extracted_min_price]
        
        # Extract non-price search terms
        search_terms = re.sub(r'(?:under|over|above|below|between|and|\d+\.?\d*|dollars?|\$)', '', query_lower)
        search_terms = ' '.join(search_terms.split())
        
        # Apply name and color filters from query
        if search_terms.strip():
            search_words = search_terms.split()
            filtered_products = [
                product for product in filtered_products
                if any(_matches_search_term(term, product) for term in search_words)
            ]

    return filtered_products
    
@mcp.tool(description="A simple tool returning file content")
async def echo(message: str, ctx: Context) -> str:

    # ctx2 = mcp.get_context()
    # print(f"Context ID: {ctx2}")

    # await ctx.debug(f"Processing file 1/3: {message}")
    await ctx.info(f"Processing file 1/3:")
    await ctx.info(f"Processing file 2/3:")
    await ctx.info(f"Processing file 3/3:")

    # await ctx.log(
    #         level="info",
    #         message="hello there",
    #         logger_name="Obi Wan",
    #     )

    return f"Here's the file content: {message}"

mcp.run(transport="streamable-http")
