from app.gen_ai import generate_text
from app.services import analytics_service

def get_response(data):
    query = data.get("message", "").strip()

    if not query:
        return {"error": "Message is required"}

    try:
        kpis = analytics_service.get_kpis() or {}
        expiry = analytics_service.get_expiry_risk() or []
        top_prod = analytics_service.get_product_performance() or []
    except Exception as e:
        print("❌ Analytics fetch error:", e)
        kpis, expiry, top_prod = {}, [], []

    # ✅ LIMIT DATA (VERY IMPORTANT)
    expiry_list = [
        f"{e.get('name','Item')} ({e.get('days','?')} days)"
        for e in expiry[:5]   # only top 5
    ]

    top_products = [
        p.get("product") or p.get("name") or "Unknown"
        for p in top_prod[:3]
    ]

    # ✅ CLEAN PROMPT (BETTER AI OUTPUT)
    prompt = f"""
You are BizMate AI, a smart retail business assistant.

Store Insights:
- Total Revenue: ₹{kpis.get('totalRevenue', 'N/A')}
- Avg Daily Sales: ₹{kpis.get('avgDaily', 'N/A')}
- Top Product: {kpis.get('topProduct', 'N/A')}
- Expiry Risks: {", ".join(expiry_list) if expiry_list else "None"}
- Top Selling Products: {", ".join(top_products) if top_products else "N/A"}

User Question:
{query}

Instructions:
- Give a short, clear answer
- Use numbers and insights
- Be business-friendly
"""

    reply = generate_text(prompt)

    # ✅ FAILSAFE
    if not reply:
        return {"reply": "Sorry, I couldn't generate a response right now."}

    return {"reply": reply}