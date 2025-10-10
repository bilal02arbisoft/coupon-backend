# populate_uae_data.py
import json
from datetime import datetime
from app.app import app, db
from app.app import Store, Coupon, Category

# -----------------------------------------------------------------------------------
# 1) Canonical categories from your attached front-end list
# -----------------------------------------------------------------------------------
BASE_CATEGORIES = [
    {"id": "electronics", "name": "Electronics & Gadgets", "description": "Smartphones, laptops, gadgets & more", "icon": "electronics-icon.png"},
    {"id": "fashion",     "name": "Fashion & Beauty",      "description": "Clothing, accessories, makeup & skincare", "icon": "fashion-icon.png"},
    {"id": "food",        "name": "Food & Delivery",       "description": "Restaurants, groceries & food delivery", "icon": "food-icon.png"},
    {"id": "home",        "name": "Home & Garden",         "description": "Furniture, decor & household items", "icon": "home-icon.png"},
    {"id": "travel",      "name": "Travel & Hotels",       "description": "Flights, hotels & travel packages", "icon": "travel-icon.png"},
    {"id": "health",      "name": "Health & Pharmacy",     "description": "Medicines, healthcare & fitness", "icon": "health-icon.png"},
]

# -----------------------------------------------------------------------------------
# 2) Stores from the attached data
# -----------------------------------------------------------------------------------
STORES = [
    {
        "id": "noon",
        "name": "Noon.com",
        "logo": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=120&h=120&fit=crop&crop=center",
        "description": ("The Middle East's leading online shopping destination offering millions of products across "
                        "electronics, fashion, beauty, home, sports, and more. Shop with confidence knowing you'll get "
                        "the best deals and fastest delivery across the UAE and Saudi Arabia."),
        "website_url": "https://noon.com",
        "affiliate_base_url": "https://noon.com",
        "rating": 4.5,
        "total_coupons": 45,
        "categories": ["electronics", "fashion", "home"],
        "social_links": {"instagram": "@noon", "twitter": "@noon"},
        "established_year": 2017,
        "headquarters": "Dubai, UAE",
        "return_policy": "15-day return policy",
        "shipping_info": "Free delivery on orders over AED 99",
    },
    {
        "id": "amazon-ae",
        "name": "Amazon.ae",
        "logo": "https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=120&h=120&fit=crop&crop=center",
        "description": ("Your trusted online shopping destination in the UAE. From electronics and books to fashion "
                        "and home essentials, find everything you need with fast delivery and excellent customer service. "
                        "Prime members enjoy free shipping and exclusive deals."),
        "website_url": "https://amazon.ae",
        "affiliate_base_url": "https://amazon.ae",
        "rating": 4.3,
        "total_coupons": 38,
        "categories": ["electronics", "books", "fashion", "home"],  # 'books' will be auto-created
        "social_links": {"instagram": "@amazonae", "twitter": "@amazonae"},
        "established_year": 2019,
        "headquarters": "Dubai, UAE",
        "return_policy": "30-day return policy",
        "shipping_info": "Free delivery with Prime",
    },
    {
        "id": "carrefour",
        "name": "Carrefour UAE",
        "logo": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=120&h=120&fit=crop&crop=center",
        "description": ("Your neighborhood hypermarket offering fresh groceries, household essentials, electronics, "
                        "and more at unbeatable prices. Shop online or visit our stores across the UAE for quality "
                        "products and convenient shopping experience."),
        "website_url": "https://carrefouruae.com",
        "affiliate_base_url": "https://carrefouruae.com",
        "rating": 4.2,
        "total_coupons": 28,
        "categories": ["grocery", "home", "electronics"],  # 'grocery' -> auto-created
        "social_links": {"instagram": "@carrefouruae", "twitter": "@carrefouruae"},
        "established_year": 1995,
        "headquarters": "Dubai, UAE",
        "return_policy": "14-day return policy",
        "shipping_info": "Same-day delivery available",
    },
    {
        "id": "namshi",
        "name": "Namshi",
        "logo": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=120&h=120&fit=crop&crop=center",
        "description": ("The ultimate fashion and lifestyle destination in the Middle East. Discover the latest trends "
                        "in clothing, shoes, bags, and accessories for men, women, and kids from top international and "
                        "regional brands."),
        "website_url": "https://namshi.com",
        "affiliate_base_url": "https://namshi.com",
        "rating": 4.4,
        "total_coupons": 52,
        "categories": ["fashion", "beauty", "accessories"],  # 'beauty', 'accessories' auto-created
        "social_links": {"instagram": "@namshi", "twitter": "@namshi"},
        "established_year": 2011,
        "headquarters": "Dubai, UAE",
        "return_policy": "30-day return policy",
        "shipping_info": "Free delivery on orders over AED 200",
    },
    {
        "id": "ounass",
        "name": "Ounass",
        "logo": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=120&h=120&fit=crop&crop=center",
        "description": ("The ultimate luxury shopping destination in the Middle East. Discover exclusive designer "
                        "collections from the world's most coveted fashion houses, premium beauty brands, and luxury "
                        "lifestyle products with personalized styling services."),
        "website_url": "https://ounass.ae",
        "affiliate_base_url": "https://ounass.ae",
        "rating": 4.6,
        "total_coupons": 18,
        "categories": ["fashion", "beauty", "luxury"],  # 'luxury' auto-created
        "social_links": {"instagram": "@ounass", "twitter": "@ounass"},
        "established_year": 2016,
        "headquarters": "Dubai, UAE",
        "return_policy": "14-day return policy",
        "shipping_info": "Free delivery on orders over AED 500",
    },
    {
        "id": "sharaf-dg",
        "name": "Sharaf DG",
        "logo": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=120&h=120&fit=crop&crop=center",
        "description": ("Your trusted electronics and technology partner in the UAE. From the latest smartphones and "
                        "laptops to gaming consoles and smart home devices, find cutting-edge technology at competitive "
                        "prices with expert advice and reliable after-sales service."),
        "website_url": "https://sharafdg.com",
        "affiliate_base_url": "https://sharafdg.com",
        "rating": 4.1,
        "total_coupons": 23,
        "categories": ["electronics", "technology", "gaming"],  # 'technology', 'gaming' auto-created
        "social_links": {"instagram": "@sharafdg", "twitter": "@sharafdg"},
        "established_year": 2005,
        "headquarters": "Dubai, UAE",
        "return_policy": "7-day return policy",
        "shipping_info": "Free delivery on orders over AED 199",
    },
    {
        "id": "talabat",
        "name": "Talabat",
        "logo": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=120&h=120&fit=crop&crop=center",
        "description": ("The Middle East's favorite food delivery app bringing you delicious meals from thousands of "
                        "restaurants. From local favorites to international cuisines, groceries to pharmacy items - all "
                        "delivered fresh to your doorstep in minutes."),
        "website_url": "https://talabat.com",
        "affiliate_base_url": "https://talabat.com",
        "rating": 4.0,
        "total_coupons": 35,
        "categories": ["food", "delivery", "restaurants"],  # 'delivery', 'restaurants' auto-created
        "social_links": {"instagram": "@talabat_uae", "twitter": "@talabat_uae"},
        "established_year": 2004,
        "headquarters": "Dubai, UAE",
        "return_policy": "Refund on app issues",
        "shipping_info": "Fast delivery within 30-45 mins",
    },
    {
        "id": "jumia",
        "name": "Jumia UAE",
        "logo": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=120&h=120&fit=crop&crop=center",
        "description": ("Your go-to online marketplace in the UAE for electronics, fashion, mobile phones, and lifestyle "
                        "products. Discover great deals from trusted sellers with secure payment options and reliable "
                        "delivery across the Emirates."),
        "website_url": "https://jumia.ae",
        "affiliate_base_url": "https://jumia.ae",
        "rating": 4.2,
        "total_coupons": 31,
        "categories": ["electronics", "fashion", "mobile"],  # 'mobile' auto-created
        "social_links": {"instagram": "@jumiauae", "twitter": "@jumiauae"},
        "established_year": 2013,
        "headquarters": "Dubai, UAE",
        "return_policy": "15-day return policy",
        "shipping_info": "Free delivery on orders over AED 150",
    },
]

# -----------------------------------------------------------------------------------
# 3) Coupons from the attached data
# -----------------------------------------------------------------------------------
COUPONS = [
    # Noon
    {
        "id": "noon-welcome25",
        "title": "25% Off First Order + Free Delivery",
        "store_id": "noon",
        "code": "WELCOME25",
        "discount_type": "percentage",
        "discount_value": 25,
        "original_price": 400,
        "discounted_price": 300,
        "currency": "AED",
        "expiry_date": "2024-12-31T23:59:59Z",
        "categories": ["electronics", "fashion", "home"],
        "terms_conditions": "Valid on first purchase. Minimum order AED 200. Not valid with other offers.",
        "usage_instructions": "1. Add items to cart 2. Enter code WELCOME25 at checkout 3. Enjoy savings!",
        "minimum_order": 200,
        "maximum_discount": 100,
        "verified": True,
        "success_rate": 0.95,
        "usage_count": 2340,
        "user_rating": 4.8,
        "featured": True,
        "deal_type": "hot",
        "applicable_products": ["All products except gift cards"],
        "exclusions": ["Gift cards", "Already discounted items"],
    },
    {
        "id": "noon-electronics50",
        "title": "Up to 50% Off Electronics",
        "store_id": "noon",
        "code": "TECH50",
        "discount_type": "percentage",
        "discount_value": 50,
        "original_price": 1000,
        "discounted_price": 500,
        "currency": "AED",
        "expiry_date": "2024-11-15T23:59:59Z",
        "categories": ["electronics"],
        "terms_conditions": "Valid on selected electronics. While stocks last.",
        "usage_instructions": "Use code TECH50 on electronics category products",
        "minimum_order": 300,
        "maximum_discount": 500,
        "verified": True,
        "success_rate": 0.92,
        "usage_count": 1856,
        "user_rating": 4.6,
        "featured": False,
        "deal_type": "new",
        "applicable_products": ["Smartphones", "Laptops", "Tablets"],
        "exclusions": ["Apple products", "Gaming consoles"],
    },

    # Amazon.ae
    {
        "id": "amazon-prime20",
        "title": "20% Off for Prime Members",
        "store_id": "amazon-ae",
        "code": "PRIME20",
        "discount_type": "percentage",
        "discount_value": 20,
        "original_price": 250,
        "discounted_price": 200,
        "currency": "AED",
        "expiry_date": "2024-11-30T23:59:59Z",
        "categories": ["electronics", "books", "fashion"],
        "terms_conditions": "Valid for Prime members only. Limited time offer.",
        "usage_instructions": "Code automatically applied for Prime members",
        "minimum_order": 100,
        "maximum_discount": 200,
        "verified": True,
        "success_rate": 0.98,
        "usage_count": 3245,
        "user_rating": 4.9,
        "featured": True,
        "deal_type": "exclusive",
        "applicable_products": ["Prime eligible items"],
        "exclusions": ["Digital products", "Subscriptions"],
    },
    {
        "id": "amazon-books15",
        "title": "15% Off All Books",
        "store_id": "amazon-ae",
        "code": "BOOKS15",
        "discount_type": "percentage",
        "discount_value": 15,
        "original_price": 150,
        "discounted_price": 127.50,
        "currency": "AED",
        "expiry_date": "2024-12-25T23:59:59Z",
        "categories": ["books"],
        "terms_conditions": "Valid on physical and digital books",
        "usage_instructions": "Enter BOOKS15 at checkout on book purchases",
        "minimum_order": 50,
        "maximum_discount": 75,
        "verified": True,
        "success_rate": 0.89,
        "usage_count": 892,
        "user_rating": 4.4,
        "featured": False,
        "deal_type": "verified",
        "applicable_products": ["Physical books", "E-books", "Audiobooks"],
        "exclusions": ["Magazines", "Newspapers"],
    },

    # Carrefour
    {
        "id": "carrefour-grocery30",
        "title": "30% Off Grocery Shopping",
        "store_id": "carrefour",
        "code": "GROCERY30",
        "discount_type": "percentage",
        "discount_value": 30,
        "original_price": 200,
        "discounted_price": 140,
        "currency": "AED",
        "expiry_date": "2024-11-20T23:59:59Z",
        "categories": ["grocery"],
        "terms_conditions": "Valid on grocery items. Minimum spend AED 150.",
        "usage_instructions": "Shop groceries worth AED 150+ and use code GROCERY30",
        "minimum_order": 150,
        "maximum_discount": 120,
        "verified": True,
        "success_rate": 0.94,
        "usage_count": 1567,
        "user_rating": 4.7,
        "featured": True,
        "deal_type": "hot",
        "applicable_products": ["Fresh produce", "Packaged foods", "Beverages"],
        "exclusions": ["Alcohol", "Tobacco", "Baby formula"],
    },

    # Namshi
    {
        "id": "namshi-fashion40",
        "title": "40% Off Fashion & Accessories",
        "store_id": "namshi",
        "code": "FASHION40",
        "discount_type": "percentage",
        "discount_value": 40,
        "original_price": 300,
        "discounted_price": 180,
        "currency": "AED",
        "expiry_date": "2024-12-15T23:59:59Z",
        "categories": ["fashion", "accessories"],
        "terms_conditions": "Valid on selected fashion items and accessories",
        "usage_instructions": "Browse fashion section and apply FASHION40 at checkout",
        "minimum_order": 200,
        "maximum_discount": 300,
        "verified": True,
        "success_rate": 0.91,
        "usage_count": 2108,
        "user_rating": 4.5,
        "featured": True,
        "deal_type": "new",
        "applicable_products": ["Clothing", "Shoes", "Bags", "Accessories"],
        "exclusions": ["Luxury brands", "Sale items"],
    },
    {
        "id": "namshi-free-shipping",
        "title": "Free Shipping on All Orders",
        "store_id": "namshi",
        "code": "FREESHIP",
        "discount_type": "free_shipping",
        "discount_value": 0,
        "original_price": 25,
        "discounted_price": 0,
        "currency": "AED",
        "expiry_date": "2024-12-31T23:59:59Z",
        "categories": ["fashion", "beauty", "accessories"],
        "terms_conditions": "Free shipping on any order value",
        "usage_instructions": "Enter FREESHIP at checkout to remove shipping charges",
        "minimum_order": 0,
        "maximum_discount": 25,
        "verified": True,
        "success_rate": 0.99,
        "usage_count": 4521,
        "user_rating": 4.8,
        "featured": False,
        "deal_type": "verified",
        "applicable_products": ["All items"],
        "exclusions": ["Express delivery"],
    },

    # Ounass
    {
        "id": "ounass-luxury20",
        "title": "20% Off Luxury Brands",
        "store_id": "ounass",
        "code": "LUXURY20",
        "discount_type": "percentage",
        "discount_value": 20,
        "original_price": 1500,
        "discounted_price": 1200,
        "currency": "AED",
        "expiry_date": "2024-11-25T23:59:59Z",
        "categories": ["luxury", "fashion", "beauty"],
        "terms_conditions": "Valid on selected luxury designer brands",
        "usage_instructions": "Shop luxury brands and apply LUXURY20 for exclusive discount",
        "minimum_order": 500,
        "maximum_discount": 1000,
        "verified": True,
        "success_rate": 0.88,
        "usage_count": 634,
        "user_rating": 4.9,
        "featured": True,
        "deal_type": "exclusive",
        "applicable_products": ["Designer clothing", "Luxury bags", "Premium beauty"],
        "exclusions": ["Limited editions", "Jewelry"],
    },

    # Sharaf DG
    {
        "id": "sharaf-gaming25",
        "title": "25% Off Gaming Gear",
        "store_id": "sharaf-dg",
        "code": "GAMING25",
        "discount_type": "percentage",
        "discount_value": 25,
        "original_price": 800,
        "discounted_price": 600,
        "currency": "AED",
        "expiry_date": "2024-12-10T23:59:59Z",
        "categories": ["gaming", "electronics"],
        "terms_conditions": "Valid on gaming consoles, accessories, and games",
        "usage_instructions": "Browse gaming section and use GAMING25 at checkout",
        "minimum_order": 300,
        "maximum_discount": 400,
        "verified": True,
        "success_rate": 0.93,
        "usage_count": 1234,
        "user_rating": 4.6,
        "featured": False,
        "deal_type": "hot",
        "applicable_products": ["Gaming consoles", "Controllers", "Games", "Headsets"],
        "exclusions": ["Pre-orders", "Digital downloads"],
    },

    # Talabat
    {
        "id": "talabat-food50",
        "title": "50 AED Off Food Orders",
        "store_id": "talabat",
        "code": "FOOD50",
        "discount_type": "fixed",
        "discount_value": 50,
        "original_price": 150,
        "discounted_price": 100,
        "currency": "AED",
        "expiry_date": "2024-11-18T23:59:59Z",
        "categories": ["food", "delivery"],
        "terms_conditions": "Valid on food orders above AED 100. Once per user.",
        "usage_instructions": "Order food worth AED 100+ and apply FOOD50",
        "minimum_order": 100,
        "maximum_discount": 50,
        "verified": True,
        "success_rate": 0.96,
        "usage_count": 3876,
        "user_rating": 4.7,
        "featured": True,
        "deal_type": "new",
        "applicable_products": ["Restaurant orders", "Groceries"],
        "exclusions": ["Delivery charges", "Service fees"],
    },
    {
        "id": "talabat-free-delivery",
        "title": "Free Delivery on First Order",
        "store_id": "talabat",
        "code": "FIRSTFREE",
        "discount_type": "free_shipping",
        "discount_value": 0,
        "original_price": 15,
        "discounted_price": 0,
        "currency": "AED",
        "expiry_date": "2024-12-31T23:59:59Z",
        "categories": ["food", "delivery"],
        "terms_conditions": "Free delivery for new customers on first order",
        "usage_instructions": "New users: Enter FIRSTFREE to waive delivery charges",
        "minimum_order": 50,
        "maximum_discount": 15,
        "verified": True,
        "success_rate": 0.97,
        "usage_count": 2945,
        "user_rating": 4.8,
        "featured": False,
        "deal_type": "verified",
        "applicable_products": ["All restaurant orders"],
        "exclusions": ["Service charges"],
    },

    # Jumia
    {
        "id": "jumia-mobile35",
        "title": "35% Off Mobile Phones",
        "store_id": "jumia",
        "code": "MOBILE35",
        "discount_type": "percentage",
        "discount_value": 35,
        "original_price": 2000,
        "discounted_price": 1300,
        "currency": "AED",
        "expiry_date": "2024-11-28T23:59:59Z",
        "categories": ["mobile", "electronics"],
        "terms_conditions": "Valid on selected smartphone brands and models",
        "usage_instructions": "Shop smartphones and apply MOBILE35 for instant savings",
        "minimum_order": 500,
        "maximum_discount": 700,
        "verified": True,
        "success_rate": 0.90,
        "usage_count": 1456,
        "user_rating": 4.4,
        "featured": False,
        "deal_type": "hot",
        "applicable_products": ["Android phones", "Accessories", "Cases"],
        "exclusions": ["iPhone", "Refurbished devices"],
    },
]

# -----------------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------------
def upsert_category(cat_id: str, name: str = None, description: str = "", icon: str = "") -> Category:
    obj = Category.query.get(cat_id)
    if obj is None:
        obj = Category(id=cat_id, name=(name or cat_id.title()), description=description or "", icon=icon or "")
        db.session.add(obj)
    else:
        # Update minimal fields if provided
        if name:
            obj.name = name
        if description:
            obj.description = description
        if icon:
            obj.icon = icon
    return obj

def attach_categories(entity, category_ids):
    """Attach many-to-many Category objects by id."""
    entity.categories.clear()
    for cid in category_ids:
        cat = Category.query.get(cid)
        if not cat:
            # Auto-create unknown categories with a reasonable display name
            cat = upsert_category(cid, name=cid.replace("-", " ").title())
        entity.categories.append(cat)

def json_str(data) -> str:
    return json.dumps(data, ensure_ascii=False) if isinstance(data, (list, dict)) else (data or "")

# -----------------------------------------------------------------------------------
# Populate functions
# -----------------------------------------------------------------------------------
def populate_categories():
    # Ensure base categories exist
    for c in BASE_CATEGORIES:
        upsert_category(c["id"], c["name"], c.get("description", ""), c.get("icon", ""))
    db.session.commit()

def populate_stores():
    for s in STORES:
        store = Store.query.get(s["id"]) or Store(id=s["id"])
        store.name = s["name"]
        store.logo = s.get("logo")
        store.description = s.get("description")
        store.website_url = s.get("website_url")
        store.rating = s.get("rating")
        store.total_coupons = s.get("total_coupons")
        store.social_links = json_str(s.get("social_links"))
        store.established_year = s.get("established_year")
        store.headquarters = s.get("headquarters")
        store.return_policy = s.get("return_policy")
        store.shipping_info = s.get("shipping_info")

        db.session.add(store)
        # Ensure categories referenced by stores exist, then attach
        for cid in s.get("categories", []):
            if not Category.query.get(cid):
                upsert_category(cid, name=cid.replace("-", " ").title())
        db.session.flush()
        attach_categories(store, s.get("categories", []))

    db.session.commit()

def populate_coupons():
    for c in COUPONS:
        coupon = Coupon.query.get(c["id"]) or Coupon(id=c["id"])
        coupon.title = c["title"]
        coupon.store_id = c["store_id"]
        coupon.code = c.get("code")
        coupon.discount_type = c.get("discount_type")
        coupon.discount_value = c.get("discount_value")
        coupon.original_price = c.get("original_price")
        coupon.discounted_price = c.get("discounted_price")
        coupon.currency = c.get("currency")
        # Parse ISO-like strings into datetime; ignore if unparsable
        exp_raw = c.get("expiry_date")
        exp_val = None
        if isinstance(exp_raw, str):
            for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    exp_val = datetime.strptime(exp_raw, fmt)
                    break
                except Exception:
                    continue
        coupon.expiry_date = exp_val
        coupon.terms_conditions = c.get("terms_conditions")
        coupon.usage_instructions = c.get("usage_instructions")
        coupon.minimum_order = c.get("minimum_order")
        coupon.maximum_discount = c.get("maximum_discount")
        coupon.verified = c.get("verified", False)
        coupon.success_rate = c.get("success_rate")
        coupon.usage_count = c.get("usage_count")
        coupon.user_rating = c.get("user_rating")
        coupon.featured = c.get("featured", False)
        coupon.deal_type = c.get("deal_type")
        coupon.applicable_products = json_str(c.get("applicable_products", []))
        coupon.exclusions = json_str(c.get("exclusions", []))

        db.session.add(coupon)

        # Ensure categories referenced by coupons exist, then attach
        for cid in c.get("categories", []):
            if not Category.query.get(cid):
                upsert_category(cid, name=cid.replace("-", " ").title())
        db.session.flush()
        attach_categories(coupon, c.get("categories", []))

    db.session.commit()

# -----------------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        populate_categories()
        populate_stores()
        populate_coupons()
        print("✅ UAE categories, stores, and coupons populated (upserted) successfully!")