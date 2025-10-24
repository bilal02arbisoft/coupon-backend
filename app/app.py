from datetime import datetime
import os
import datetime as dt

from flask import Flask, jsonify, redirect, url_for, request, flash, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# --- NEW: Flask-Admin imports ---
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import ImageUploadField
from wtforms import DateField
from wtforms.fields.html5 import DateTimeLocalField

# If you want simple HTTP Basic auth for /admin, uncomment these lines and the protected views below
from flask_httpauth import HTTPBasicAuth
# --- NEW: auth libs ---
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.simple import PasswordField, BooleanField, StringField
from wtforms.validators import DataRequired

auth = HTTPBasicAuth()
USERS = {"admin": "change-me"}  # Replace with something real or wire up Flask-Login/Flask-Security
@auth.verify_password
def verify_password(username, password):
    if USERS.get(username) == password:
        return username
    return None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://myapp:REPLACE_ME_STRONG@/myappdb?host=/var/run/postgresql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'replace-this-in-prod'  # Needed by Flask‑Admin for forms/CSRF
app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')  # persisted locally alongside DB

# Ensure upload directories exist (instance/uploads/{stores,categories})
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'stores'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'categories'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'banners'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'blogs'), exist_ok=True)

# Allow all origins, methods, and headers
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


# Association Table for Store-Category many-to-many relationship
store_category = db.Table('store_category',
    db.Column('store_id', db.String(100), db.ForeignKey('stores.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.String(100), db.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)

# Association Table for Coupon-Category many-to-many relationship
coupon_category = db.Table('coupon_category',
    db.Column('coupon_id', db.String(100), db.ForeignKey('coupons.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.String(100), db.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)

class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(200))
    description = db.Column(db.String(255))
    website_url = db.Column(db.String(200))
    rating = db.Column(db.Float)
    total_coupons = db.Column(db.Integer)
    social_links = db.Column(db.String(200))
    established_year = db.Column(db.Integer)
    headquarters = db.Column(db.String(100))
    return_policy = db.Column(db.String(100))
    shipping_info = db.Column(db.String(100))

    # Many-to-many relationship with categories
    categories = db.relationship('Category', secondary=store_category, backref=db.backref('stores', lazy='dynamic'))

    def __repr__(self):
        return f'<Store {self.name}>'

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    store_id = db.Column(db.String(100), db.ForeignKey('stores.id'), nullable=False)
    code = db.Column(db.String(100))
    discount_type = db.Column(db.String(50))
    discount_value = db.Column(db.Float)
    original_price = db.Column(db.Float)
    discounted_price = db.Column(db.Float)
    currency = db.Column(db.String(20))
    # Expiry as true DateTime
    expiry_date = db.Column(db.DateTime)
    terms_conditions = db.Column(db.String(255))
    usage_instructions = db.Column(db.String(255))
    minimum_order = db.Column(db.Float)
    maximum_discount = db.Column(db.Float)
    verified = db.Column(db.Boolean)
    success_rate = db.Column(db.Float)
    usage_count = db.Column(db.Integer)
    user_rating = db.Column(db.Float)
    featured = db.Column(db.Boolean)
    deal_type = db.Column(db.String(50))
    applicable_products = db.Column(db.String(255))
    exclusions = db.Column(db.String(255))
    # New flags
    hot_deal = db.Column(db.Boolean, default=False, nullable=False)
    show_on_homepage = db.Column(db.Boolean, default=False, nullable=False)

    # Many-to-many relationship with categories
    categories = db.relationship('Category', secondary=coupon_category, backref=db.backref('coupons', lazy='dynamic'))

    def __repr__(self):
        return f'<Coupon {self.title}>'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(200))  # Optionally, store icon URL or file path

    def __repr__(self):
        return f'<Category {self.name}>'

# Simple banner model for homepage/sections with image and click-through URL
class Banner(db.Model):
    __tablename__ = 'banners'

    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.String(200))  # stored filename for uploaded banner image
    url = db.Column(db.String(255))   # target URL when banner is clicked

    def __repr__(self):
        return f'<Banner {self.id}>'

# About content model for company/about page
class About(db.Model):
    __tablename__ = 'about'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200))
    legal_form = db.Column(db.String(200))
    founded_year = db.Column(db.Integer)
    our_story = db.Column(db.Text)  # long text
    location = db.Column(db.Text)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    mission = db.Column(db.Text)
    vision = db.Column(db.Text)
    privacy_note = db.Column(db.Text)
    disclaimer = db.Column(db.Text)
    last_updated = db.Column(db.String(50))  # e.g., "October 2024"

    def __repr__(self):
        return f'<About {self.company_name or self.id}>'

# Blog model for articles/news
class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, index=True, nullable=False)
    image = db.Column(db.String(255))  # can be URL or uploaded filename under instance/uploads/blogs
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    date = db.Column(db.Date)
    author = db.Column(db.String(120))
    read_time = db.Column(db.String(50))
    tags = db.Column(db.Text)  # comma-separated values

    def __repr__(self):
        return f'<Blog {self.slug}>'
# Public route to serve uploaded images from instance/uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



login_manager = LoginManager(app)
login_manager.login_view = "login"  # where to redirect when not authed

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Admin Login</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-md-4">
      <div class="card shadow-sm">
        <div class="card-body">
          <h4 class="mb-3">Sign in</h4>
          {% with msgs = get_flashed_messages() %}
            {% if msgs %}
              <div class="alert alert-danger">{{ msgs[0] }}</div>
            {% endif %}
          {% endwith %}
          <form method="post">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input class="form-control" name="username" required autofocus>
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input class="form-control" type="password" name="password" required>
            </div>
            <button class="btn btn-primary w-100">Sign in</button>
          </form>
          <p class="text-muted mt-3 mb-0" style="font-size: .9rem;">
            Tip: create your first user via CLI (see README in code comments).
          </p>
        </div>
      </div>
      <p class="text-center mt-3"><a href="{{ url_for('index_redirect') }}">&larr; Back</a></p>
    </div>
  </div>
</div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_url = request.args.get("next") or url_for("admin.index")
            return redirect(next_url)
        flash("Invalid username or password.")
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
# -------------------- API ROUTES (unchanged) --------------------
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    categories_data = []
    for category in categories:
        # Build icon URL if it's an uploaded file (stored as filename inside categories/)
        icon_value = category.icon
        if icon_value and not (str(icon_value).startswith('http://') or str(icon_value).startswith('https://') or str(icon_value).startswith('/')):
            icon_value = url_for('uploaded_file', filename=f"categories/{icon_value}", _external=True)

        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "icon": icon_value
        })
    return jsonify(categories_data)


@app.route('/api/stores', methods=['GET'])
def get_stores():
    stores = Store.query.all()
    stores_data = []
    for store in stores:
        # Build logo URL if it's an uploaded file (stored as filename inside stores/)
        logo_value = store.logo
        if logo_value and not (str(logo_value).startswith('http://') or str(logo_value).startswith('https://') or str(logo_value).startswith('/')):
            logo_value = url_for('uploaded_file', filename=f"stores/{logo_value}", _external=True)

        stores_data.append({
            "id": store.id,
            "name": store.name,
            "logo": logo_value,
            "description": store.description,
            "website_url": store.website_url,
            "rating": store.rating,
            "total_coupons": store.total_coupons,
            "categories": [category.name for category in store.categories],
            "social_links": store.social_links,
            "established_year": store.established_year,
            "headquarters": store.headquarters,
            "return_policy": store.return_policy,
            "shipping_info": store.shipping_info
        })
    return jsonify(stores_data)


@app.route('/api/coupons', methods=['GET'])
def get_coupons():
    coupons = Coupon.query.all()
    coupons_data = []
    for coupon in coupons:
        coupons_data.append({
            "id": coupon.id,
            "title": coupon.title,
            "store_id": coupon.store_id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "original_price": coupon.original_price,
            "discounted_price": coupon.discounted_price,
            "currency": coupon.currency,
            "expiry_date": coupon.expiry_date.isoformat() if coupon.expiry_date else None,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
            "hot_deal": coupon.hot_deal,
            "show_on_homepage": coupon.show_on_homepage,
            "success_rate": coupon.success_rate,
            "usage_count": coupon.usage_count,
            "user_rating": coupon.user_rating,
            "featured": coupon.featured,
            "deal_type": coupon.deal_type,
            "applicable_products": coupon.applicable_products,
            "exclusions": coupon.exclusions
        })
    return jsonify(coupons_data)


@app.route('/api/coupons/store/<store_id>', methods=['GET'])
def get_coupons_by_store(store_id):
    coupons = Coupon.query.filter_by(store_id=store_id).all()
    coupons_data = []
    for coupon in coupons:
        coupons_data.append({
            "id": coupon.id,
            "title": coupon.title,
            "store_id": coupon.store_id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "original_price": coupon.original_price,
            "discounted_price": coupon.discounted_price,
            "currency": coupon.currency,
            "expiry_date": coupon.expiry_date.isoformat() if coupon.expiry_date else None,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
            "hot_deal": coupon.hot_deal,
            "show_on_homepage": coupon.show_on_homepage,
            "success_rate": coupon.success_rate,
            "usage_count": coupon.usage_count,
            "user_rating": coupon.user_rating,
            "featured": coupon.featured,
            "deal_type": coupon.deal_type,
            "applicable_products": coupon.applicable_products,
            "exclusions": coupon.exclusions
        })
    return jsonify(coupons_data)


@app.route('/api/coupons/category/<category_name>', methods=['GET'])
def get_coupons_by_category(category_name):
    category = Category.query.filter_by(id=category_name).first()
    if not category:
        return jsonify({"message": "Category not found"}), 404

    coupons = Coupon.query.filter(Coupon.categories.any(id=category.id)).all()
    coupons_data = []
    for coupon in coupons:
        coupons_data.append({
            "id": coupon.id,
            "title": coupon.title,
            "store_id": coupon.store_id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "original_price": coupon.original_price,
            "discounted_price": coupon.discounted_price,
            "currency": coupon.currency,
            "expiry_date": coupon.expiry_date.isoformat() if coupon.expiry_date else None,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
            "hot_deal": coupon.hot_deal,
            "show_on_homepage": coupon.show_on_homepage,
            "success_rate": coupon.success_rate,
            "usage_count": coupon.usage_count,
            "user_rating": coupon.user_rating,
            "featured": coupon.featured,
            "deal_type": coupon.deal_type,
            "applicable_products": coupon.applicable_products,
            "exclusions": coupon.exclusions
        })
    return jsonify(coupons_data)


@app.route('/api/coupons/expiring', methods=['GET'])
def get_expiring_coupons():
    cutoff_date = datetime.utcnow() + dt.timedelta(days=7)
    coupons = Coupon.query.filter(Coupon.expiry_date.isnot(None), Coupon.expiry_date <= cutoff_date).all()

    coupons_data = []
    for coupon in coupons:
        coupons_data.append({
            "id": coupon.id,
            "title": coupon.title,
            "store_id": coupon.store_id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "original_price": coupon.original_price,
            "discounted_price": coupon.discounted_price,
            "currency": coupon.currency,
            "expiry_date": coupon.expiry_date.isoformat() if coupon.expiry_date else None,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
            "hot_deal": coupon.hot_deal,
            "show_on_homepage": coupon.show_on_homepage,
            "success_rate": coupon.success_rate,
            "usage_count": coupon.usage_count,
            "user_rating": coupon.user_rating,
            "featured": coupon.featured,
            "deal_type": coupon.deal_type,
            "applicable_products": coupon.applicable_products,
            "exclusions": coupon.exclusions
        })
    return jsonify(coupons_data)


@app.route('/api/stores/count', methods=['GET'])
def get_total_stores_count():
    total_stores = Store.query.count()
    return jsonify({"total_stores": total_stores})


@app.route('/api/coupons/count', methods=['GET'])
def get_total_coupons_count():
    total_coupons = Coupon.query.count()
    return jsonify({"total_coupons": total_coupons})


@app.route('/api/coupons/hot', methods=['GET'])
def get_hot_coupons():
    coupons = Coupon.query.filter_by(hot_deal=True).all()
    data = []
    for coupon in coupons:
        data.append({
            "id": coupon.id,
            "title": coupon.title,
            "store_id": coupon.store_id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "original_price": coupon.original_price,
            "discounted_price": coupon.discounted_price,
            "currency": coupon.currency,
            "expiry_date": coupon.expiry_date.isoformat() if coupon.expiry_date else None,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
            "hot_deal": coupon.hot_deal,
            "show_on_homepage": coupon.show_on_homepage,
            "success_rate": coupon.success_rate,
            "usage_count": coupon.usage_count,
            "user_rating": coupon.user_rating,
            "featured": coupon.featured,
            "deal_type": coupon.deal_type,
            "applicable_products": coupon.applicable_products,
            "exclusions": coupon.exclusions
        })
    return jsonify(data)


@app.route('/api/coupons/homepage', methods=['GET'])
def get_homepage_coupons():
    coupons = Coupon.query.filter_by(show_on_homepage=True).all()
    data = []
    for coupon in coupons:
        data.append({
            "id": coupon.id,
            "title": coupon.title,
            "store_id": coupon.store_id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "original_price": coupon.original_price,
            "discounted_price": coupon.discounted_price,
            "currency": coupon.currency,
            "expiry_date": coupon.expiry_date,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
            "hot_deal": coupon.hot_deal,
            "show_on_homepage": coupon.show_on_homepage,
            "success_rate": coupon.success_rate,
            "usage_count": coupon.usage_count,
            "user_rating": coupon.user_rating,
            "featured": coupon.featured,
            "deal_type": coupon.deal_type,
            "applicable_products": coupon.applicable_products,
            "exclusions": coupon.exclusions
        })
    return jsonify(data)

# Single about document fetch
@app.route('/api/about', methods=['GET'])
def get_about():
    # Fetch first (or only) about entry
    about = About.query.order_by(About.id.asc()).first()
    if not about:
        return jsonify({}), 200
    return jsonify({
        "company_name": about.company_name,
        "legal_form": about.legal_form,
        "founded_year": about.founded_year,
        "our_story": about.our_story,
        "location": about.location,
        "phone": about.phone,
        "email": about.email,
        "website": about.website,
        "mission": about.mission,
        "vision": about.vision,
        "privacy_note": about.privacy_note,
        "disclaimer": about.disclaimer,
        "last_updated": about.last_updated,
    })


# List banners with absolute image URLs
@app.route('/api/banners', methods=['GET'])
def get_banners():
    banners = Banner.query.all()
    data = []
    for b in banners:
        logo_value = b.logo
        if logo_value and not (str(logo_value).startswith('http://') or str(logo_value).startswith('https://') or str(logo_value).startswith('/')):
            logo_value = url_for('uploaded_file', filename=f"banners/{logo_value}", _external=True)
        data.append({
            "id": b.id,
            "logo": logo_value,
            "url": b.url,
        })
    return jsonify(data)


# List blogs
@app.route('/api/blogs', methods=['GET'])
def get_blogs():
    blogs = Blog.query.order_by(Blog.date.desc().nullslast()).all()
    data = []
    for b in blogs:
        image_value = b.image
        if image_value and not (str(image_value).startswith('http://') or str(image_value).startswith('https://') or str(image_value).startswith('/')):
            image_value = url_for('uploaded_file', filename=f"blogs/{image_value}", _external=True)
        tags_list = []
        if b.tags:
            tags_list = [t.strip() for t in str(b.tags).split(',') if t.strip()]
        data.append({
            "id": b.id,
            "title": b.title,
            "slug": b.slug,
            "image": image_value,
            "description": b.description,
            "content": b.content,
            "date": b.date.isoformat() if b.date else None,
            "author": b.author,
            "readTime": b.read_time,
            "tags": tags_list,
        })
    return jsonify(data)


# -------------------- ADMIN PANEL --------------------

class SecureModelView(ModelView):
    """Hardened base for admin views: login required + small quality-of-life tweaks."""
    can_view_details = True
    create_modal = True
    edit_modal = True
    column_display_all_relations = True
    page_size = 25
    column_default_sort = ('id', False)

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, "is_admin", False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))


class StoreAdmin(SecureModelView):
    column_list = [
        'id', 'name', 'logo', 'website_url', 'rating', 'total_coupons', 'established_year', 'headquarters', 'categories'
    ]
    column_searchable_list = ['id', 'name', 'description', 'website_url', 'headquarters']
    column_filters = ['rating', 'total_coupons', 'established_year', 'categories']
    form_columns = [
        'id', 'name', 'logo', 'description', 'website_url', 'rating', 'total_coupons', 'social_links',
        'established_year', 'headquarters', 'return_policy', 'shipping_info', 'categories'
    ]

    # Save uploaded logos to instance/uploads/stores and store filename in DB
    form_extra_fields = {
        'logo': ImageUploadField('Logo',
                                 base_path=os.path.join(app.config['UPLOAD_FOLDER'], 'stores'),
                                 allow_overwrite=False)
    }


class CategoryAdmin(SecureModelView):
    column_list = ['id', 'name', 'description', 'icon']
    column_searchable_list = ['id', 'name', 'description']
    form_columns = ['id', 'name', 'description', 'icon']

    # Save uploaded icons to instance/uploads/categories and store filename in DB
    form_extra_fields = {
        'icon': ImageUploadField('Icon',
                                 base_path=os.path.join(app.config['UPLOAD_FOLDER'], 'categories'),
                                 allow_overwrite=False)
    }


class BannerAdmin(SecureModelView):
    column_list = ['id', 'logo', 'url']
    column_searchable_list = ['url']
    form_columns = ['logo', 'url']

    # Save uploaded banner images to instance/uploads/banners and store filename in DB
    form_extra_fields = {
        'logo': ImageUploadField('Banner Image',
                                 base_path=os.path.join(app.config['UPLOAD_FOLDER'], 'banners'),
                                 allow_overwrite=False)
    }


class CouponAdmin(SecureModelView):
    column_list = [
        'id', 'title', 'store_id', 'code', 'discount_type', 'discount_value', 'currency',
        'expiry_date', 'verified', 'featured', 'hot_deal', 'show_on_homepage', 'deal_type', 'success_rate', 'usage_count', 'user_rating', 'categories'
    ]
    column_searchable_list = ['id', 'title', 'code', 'deal_type', 'terms_conditions', 'usage_instructions']
    column_filters = [
        'store_id', 'discount_type', 'currency', 'verified', 'featured', 'hot_deal', 'show_on_homepage', 'deal_type', 'categories'
    ]

    form_columns = [
        'id', 'title', 'store_id', 'code', 'discount_type', 'discount_value', 'original_price', 'discounted_price',
        'currency', 'expiry_date', 'terms_conditions', 'usage_instructions', 'minimum_order', 'maximum_discount',
        'verified', 'hot_deal', 'show_on_homepage', 'success_rate', 'usage_count', 'user_rating', 'featured', 'deal_type', 'applicable_products',
        'exclusions', 'categories'
    ]

    # Present expiry_date as HTML5 datetime-local
    def scaffold_form(self):
        form_class = super().scaffold_form()
        # HTML5 datetime-local (no timezone); store naive datetime in DB
        form_class.expiry_date = DateTimeLocalField('Expiry Date/Time', format='%Y-%m-%dT%H:%M', default=None)
        return form_class

    def on_form_prefill(self, form, id):
        model = self.get_one(id)
        if model:
            form.expiry_date.data = model.expiry_date
        return super().on_form_prefill(form, id)

    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'expiry_date'):
            model.expiry_date = form.expiry_date.data or None
        return super().on_model_change(form, model, is_created)

# Admin for Blog model
class BlogAdmin(SecureModelView):
    column_list = ['id', 'title', 'slug', 'date', 'author', 'read_time']
    column_searchable_list = ['title', 'slug', 'author', 'description', 'content']
    column_filters = ['date', 'author']
    form_columns = ['title', 'slug', 'image', 'description', 'content', 'date', 'author', 'read_time', 'tags']

    form_extra_fields = {
        'image': ImageUploadField('Image',
                                  base_path=os.path.join(app.config['UPLOAD_FOLDER'], 'blogs'),
                                  allow_overwrite=False)
    }

    def on_model_change(self, form, model, is_created):
        # ensure slug populated from title if missing
        if not model.slug and model.title:
            model.slug = "-".join(model.title.lower().split())
        return super().on_model_change(form, model, is_created)

# --- NEW: Manage Users inside Admin ---
class UserAdmin(SecureModelView):
    column_list = ['id', 'username', 'is_admin']
    column_searchable_list = ['id', 'username']
    column_filters = ['is_admin']
    form_excluded_columns = ['password_hash']
    form_extra_fields = {
        'username': StringField('Username', validators=[DataRequired()]),
        'password': PasswordField('Password (leave blank to keep current)'),
        'is_admin': BooleanField('Is Admin')
    }

    def on_model_change(self, form, model, is_created):
        # Hash password if a new one was supplied
        new_password = getattr(form, 'password').data if hasattr(form, 'password') else None
        if is_created:
            if not new_password:
                raise ValueError("Password is required when creating a user.")
            model.set_password(new_password)
        else:
            if new_password:  # only change if provided
                model.set_password(new_password)
        return super().on_model_change(form, model, is_created)

class DashboardView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, "is_admin", False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))

    @expose('/')
    def index(self):
        store_count = Store.query.count()
        coupon_count = Coupon.query.count()
        category_count = Category.query.count()
        # Render the default index with some quick stats
        return self.render('admin/index.html',
                           store_count=store_count,
                           coupon_count=coupon_count,
                           category_count=category_count)

# Create admin and register views
admin = Admin(app, name='Coupons Admin', template_mode='bootstrap4', index_view=DashboardView())
admin.add_view(StoreAdmin(Store, db.session, category='Models'))
admin.add_view(CouponAdmin(Coupon, db.session, category='Models'))
admin.add_view(CategoryAdmin(Category, db.session, category='Models'))
admin.add_view(BannerAdmin(Banner, db.session, category='Content'))
admin.add_view(BlogAdmin(Blog, db.session, category='Content'))
class AboutAdmin(SecureModelView):
    can_create = True
    can_delete = True
    column_list = ['company_name', 'legal_form', 'founded_year', 'phone', 'email', 'website', 'last_updated']
    form_columns = ['company_name', 'legal_form', 'founded_year', 'our_story', 'location', 'phone', 'email', 'website', 'mission', 'vision', 'privacy_note', 'disclaimer', 'last_updated']

admin.add_view(AboutAdmin(About, db.session, category='Content'))
admin.add_view(UserAdmin(User, db.session, category='Security'))  # <- NEW

# --- Minimal Jinja template for the admin dashboard quick stats ---
from jinja2 import DictLoader, ChoiceLoader
app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    DictLoader({
        'admin/index.html': """
        {% extends 'admin/master.html' %}
        {% block body %}
            <div class="container mt-4">
                <div class="d-flex justify-content-between align-items-center">
                    <h3>Coupons Admin – Overview</h3>
                    <div>
                        {% if current_user.is_authenticated %}
                          <span class="me-3">Hello, {{ current_user.username }}</span>
                          <a class="btn btn-sm btn-outline-secondary" href="{{ url_for('logout') }}">Logout</a>
                        {% endif %}
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Stores</h5>
                                <p class="card-text display-6">{{ store_count }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Coupons</h5>
                                <p class="card-text display-6">{{ coupon_count }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Categories</h5>
                                <p class="card-text display-6">{{ category_count }}</p>
                            </div>
                        </div>
                    </div>
                </div>
                <hr/>
                {{ super() }}
            </div>
        {% endblock %}
        """
    })
])

# Optional: convenience redirect from root to /admin
@app.route('/')
def index_redirect():
    return redirect(url_for('admin.index'))
# -------------------- How to run --------------------
# 1) pip install -U flask flask_sqlalchemy flask_migrate flask_cors flask-admin wtforms
#    (Optionally: flask-httpauth for BasicAuth or flask-login/flask-security for richer auth.)
# 2) flask db init && flask db migrate -m "init" && flask db upgrade
# 3) flask run  (or python app_with_admin.py)