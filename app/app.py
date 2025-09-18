from datetime import datetime
import datetime as dt

from flask import Flask, jsonify, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# --- NEW: Flask-Admin imports ---
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from wtforms import DateField

# If you want simple HTTP Basic auth for /admin, uncomment these lines and the protected views below
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
USERS = {"admin": "change-me"}  # Replace with something real or wire up Flask-Login/Flask-Security
@auth.verify_password
def verify_password(username, password):
    if USERS.get(username) == password:
        return username
    return None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coupons_stores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'replace-this-in-prod'  # Needed by Flask‑Admin for forms/CSRF

# Allow all origins, methods, and headers
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    # NOTE: your schema stores expiry_date as a STRING. We'll keep DB as-is but make the admin form a real date.
    expiry_date = db.Column(db.String(20))
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

# -------------------- API ROUTES (unchanged) --------------------
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    categories_data = []
    for category in categories:
        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "icon": category.icon
        })
    return jsonify(categories_data)


@app.route('/api/stores', methods=['GET'])
def get_stores():
    stores = Store.query.all()
    stores_data = []
    for store in stores:
        stores_data.append({
            "id": store.id,
            "name": store.name,
            "logo": store.logo,
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
            "expiry_date": coupon.expiry_date,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
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
            "expiry_date": coupon.expiry_date,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
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
            "expiry_date": coupon.expiry_date,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
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
    cutoff_date = datetime.utcnow() + dt.timedelta(days=7)  # Coupons expiring in the next 7 days
    # Since expiry_date is a string, attempt to parse as ISO date first; fallback to include none.
    coupons = []
    for c in Coupon.query.all():
        try:
            exp = datetime.fromisoformat(c.expiry_date)
            if exp <= cutoff_date:
                coupons.append(c)
        except Exception:
            # Skip unparsable dates
            continue

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
            "expiry_date": coupon.expiry_date,
            "categories": [category.name for category in coupon.categories],
            "terms_conditions": coupon.terms_conditions,
            "usage_instructions": coupon.usage_instructions,
            "minimum_order": coupon.minimum_order,
            "maximum_discount": coupon.maximum_discount,
            "verified": coupon.verified,
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


# -------------------- ADMIN PANEL --------------------

class SecureModelView(ModelView):
    """Minimal hardening: search, filters, column order, and a place for auth.
    Swap to Flask-Login/Flask-Security as needed.
    """

    # Uncomment for basic HTTP auth
    # def is_accessible(self):
    #     # With flask_httpauth you would wrap views instead; for Flask-Login, check current_user.is_authenticated
    #     user = auth.current_user()
    #     return user is not None

    can_view_details = True
    create_modal = True
    edit_modal = True
    column_display_all_relations = True
    page_size = 25

    # Nice default formatters
    column_default_sort = ('id', False)


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


class CategoryAdmin(SecureModelView):
    column_list = ['id', 'name', 'description', 'icon']
    column_searchable_list = ['id', 'name', 'description']
    form_columns = ['id', 'name', 'description', 'icon']


class CouponAdmin(SecureModelView):
    column_list = [
        'id', 'title', 'store_id', 'code', 'discount_type', 'discount_value', 'currency',
        'expiry_date', 'verified', 'featured', 'deal_type', 'success_rate', 'usage_count', 'user_rating', 'categories'
    ]
    column_searchable_list = ['id', 'title', 'code', 'deal_type', 'terms_conditions', 'usage_instructions']
    column_filters = [
        'store_id', 'discount_type', 'currency', 'verified', 'featured', 'deal_type', 'categories'
    ]

    form_columns = [
        'id', 'title', 'store_id', 'code', 'discount_type', 'discount_value', 'original_price', 'discounted_price',
        'currency', 'expiry_date', 'terms_conditions', 'usage_instructions', 'minimum_order', 'maximum_discount',
        'verified', 'success_rate', 'usage_count', 'user_rating', 'featured', 'deal_type', 'applicable_products',
        'exclusions', 'categories'
    ]

    # Present expiry_date as a real date picker but store as ISO string to keep your DB schema unchanged
    def scaffold_form(self):
        form_class = super().scaffold_form()
        # Replace default StringField with DateField (HTML5 date picker)
        form_class.expiry_date = DateField('Expiry Date', format='%Y-%m-%d', description='YYYY-MM-DD', default=None)
        return form_class

    def on_form_prefill(self, form, id):
        # When editing, WTForms DateField expects a date object; your DB stores a string.
        model = self.get_one(id)
        if model and isinstance(model.expiry_date, str) and model.expiry_date:
            try:
                form.expiry_date.data = datetime.strptime(model.expiry_date, '%Y-%m-%d').date()
            except Exception:
                form.expiry_date.data = None
        return super().on_form_prefill(form, id)

    def on_model_change(self, form, model, is_created):
        # Convert the DateField value back into ISO string in the DB model
        if hasattr(form, 'expiry_date') and form.expiry_date.data:
            model.expiry_date = form.expiry_date.data.strftime('%Y-%m-%d')
        else:
            model.expiry_date = None
        return super().on_model_change(form, model, is_created)


class DashboardView(AdminIndexView):
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


# --- Minimal Jinja template for the admin dashboard quick stats ---
# If you don't have a templates folder set up, this snippet uses Flask's in-memory loader pattern.
from jinja2 import DictLoader, ChoiceLoader
app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    DictLoader({
        'admin/index.html': """
        {% extends 'admin/master.html' %}
        {% block body %}
            <div class="container mt-4">
                <h3>Coupons Admin – Overview</h3>
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