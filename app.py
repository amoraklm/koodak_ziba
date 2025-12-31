from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jdatetime

app = Flask(__name__)
app.secret_key = 'kokad_ziba_secret_key_2024_alireza'

# Data directory
DATA_DIR = 'data'
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Helper function for Persian date
def get_jalali_date():
    return jdatetime.datetime.now().strftime('%Y/%m/%d')

def get_jalali_datetime():
    return jdatetime.datetime.now().strftime('%Y/%m/%d - %H:%M')

def jalali_to_gregorian(jalali_date):
    try:
        parts = jalali_date.split('/')
        jdate = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
        return jdate.togregorian()
    except:
        return None

def gregorian_to_jalali(greg_date):
    try:
        jdate = jdatetime.date.fromgregorian(date=greg_date)
        return jdate.strftime('%Y/%m/%d')
    except:
        return None

# Initialize data files
def init_data_files():
    if not os.path.exists(PRODUCTS_FILE):
        default_products = [
            {
                "id": 1,
                "name": "پیراهن گلدار دخترانه",
                "price": 450000,
                "category": "girls",
                "age_group": "3-5 سال",
                "sizes": ["2-3 سال", "3-4 سال", "4-5 سال"],
                "colors": ["صورتی", "سفید", "آبی روشن"],
                "description": "پیراهن گلدار زیبا مناسب فصل بهار و تابستان. جنس نخ پنبه با کیفیت بالا و راحت برای کودک.",
                "image": "https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=400",
                "stock": 25,
                "has_discount": True,
                "discount_percent": 20,
                "discount_start": "1403/10/01",
                "discount_end": "1403/10/30",
                "created_at": "1403/09/15"
            },
            {
                "id": 2,
                "name": "کاپشن جین پسرانه",
                "price": 680000,
                "category": "boys",
                "age_group": "6-8 سال",
                "sizes": ["5-6 سال", "6-7 سال", "7-8 سال"],
                "colors": ["آبی", "آبی تیره"],
                "description": "کاپشن جین شیک و مقاوم برای پسرها. مناسب برای استفاده روزمره و مهمانی.",
                "image": "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=400",
                "stock": 15,
                "has_discount": False,
                "discount_percent": 0,
                "discount_start": "",
                "discount_end": "",
                "created_at": "1403/09/16"
            },
            {
                "id": 3,
                "name": "تیشرت یونیکورن",
                "price": 280000,
                "category": "girls",
                "age_group": "2-4 سال",
                "sizes": ["1-2 سال", "2-3 سال", "3-4 سال"],
                "colors": ["صورتی", "بنفش", "سفید"],
                "description": "تیشرت با طرح یونیکورن که هر دختر کوچولویی عاشقش میشه. جنس نخ پنبه ارگانیک.",
                "image": "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=400",
                "stock": 30,
                "has_discount": True,
                "discount_percent": 15,
                "discount_start": "1403/10/01",
                "discount_end": "1403/10/15",
                "created_at": "1403/09/17"
            },
            {
                "id": 4,
                "name": "ست لباس خواب دایناسور",
                "price": 350000,
                "category": "boys",
                "age_group": "4-6 سال",
                "sizes": ["3-4 سال", "4-5 سال", "5-6 سال"],
                "colors": ["سبز", "آبی"],
                "description": "ست لباس خواب با طرح دایناسور برای ماجراجویی‌های شبانه! جنس نرم و راحت.",
                "image": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400",
                "stock": 20,
                "has_discount": False,
                "discount_percent": 0,
                "discount_start": "",
                "discount_end": "",
                "created_at": "1403/09/18"
            },
            {
                "id": 5,
                "name": "سرهمی نوزادی",
                "price": 320000,
                "category": "baby",
                "age_group": "0-12 ماه",
                "sizes": ["0-3 ماه", "3-6 ماه", "6-9 ماه", "9-12 ماه"],
                "colors": ["سفید", "صورتی", "آبی", "زرد"],
                "description": "سرهمی نوزادی با رنگ‌های پاستلی دلنشین. جنس نرم و لطیف مناسب پوست حساس نوزاد.",
                "image": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400",
                "stock": 40,
                "has_discount": True,
                "discount_percent": 10,
                "discount_start": "1403/10/01",
                "discount_end": "1403/10/20",
                "created_at": "1403/09/19"
            },
            {
                "id": 6,
                "name": "دامن توتو پرنسسی",
                "price": 290000,
                "category": "girls",
                "age_group": "3-5 سال",
                "sizes": ["2-3 سال", "3-4 سال", "4-5 سال"],
                "colors": ["صورتی", "بنفش", "طلایی"],
                "description": "دامن توتو براق مخصوص مهمانی‌ها و جشن‌ها. هر دختری با این دامن احساس پرنسس بودن میکنه!",
                "image": "https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=400",
                "stock": 18,
                "has_discount": False,
                "discount_percent": 0,
                "discount_start": "",
                "discount_end": "",
                "created_at": "1403/09/20"
            }
        ]
        save_products(default_products)
    
    if not os.path.exists(USERS_FILE):
        default_users = [
            {
                "id": 1,
                "username": "ادمین",
                "email": "KoodakZiba_Admin@gmail.com",
                "password": generate_password_hash("Admin_Alireza"),
                "phone": "09123456789",
                "is_admin": True,
                "created_at": "1403/09/01 - 10:00"
            }
        ]
        save_users(default_users)

# Data functions
def load_products():
    try:
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def get_discounted_price(product):
    if product.get('has_discount') and product.get('discount_percent'):
        try:
            today = jdatetime.date.today()
            start_parts = product['discount_start'].split('/')
            end_parts = product['discount_end'].split('/')
            
            start_date = jdatetime.date(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
            end_date = jdatetime.date(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))
            
            if start_date <= today <= end_date:
                discount = product['discount_percent']
                original_price = product['price']
                discounted_price = original_price - (original_price * discount / 100)
                return int(discounted_price)
        except:
            pass
    return None

def is_discount_active(product):
    if product.get('has_discount') and product.get('discount_percent'):
        try:
            today = jdatetime.date.today()
            start_parts = product['discount_start'].split('/')
            end_parts = product['discount_end'].split('/')
            
            start_date = jdatetime.date(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]))
            end_date = jdatetime.date(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]))
            
            return start_date <= today <= end_date
        except:
            pass
    return False

# Initialize data
init_data_files()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('لطفاً برای دسترسی به این صفحه وارد شوید.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('لطفاً برای دسترسی به این صفحه وارد شوید.', 'warning')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('شما دسترسی ادمین ندارید.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor
@app.context_processor
def utility_processor():
    cart = session.get('cart', [])
    return {
        'cart_count': len(cart),
        'get_discounted_price': get_discounted_price,
        'is_discount_active': is_discount_active,
        'current_jalali_date': get_jalali_date()
    }

# Template filter for formatting price
@app.template_filter('format_price')
def format_price(value):
    try:
        return "{:,}".format(int(value))
    except:
        return value

# Routes
@app.route('/')
def index():
    products = load_products()
    category = request.args.get('category', 'all')
    if category != 'all':
        products = [p for p in products if p['category'] == category]
    return render_template('index.html', products=products, current_category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('محصول یافت نشد.', 'danger')
        return redirect(url_for('index'))
    return render_template('product_detail.html', product=product)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash('پیام شما با موفقیت ارسال شد! به زودی با شما تماس می‌گیریم.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    products = load_products()
    cart_products = []
    total = 0
    
    for item in cart_items:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            # Calculate price with discount
            price = get_discounted_price(product) or product['price']
            cart_product = {
                **product,
                'quantity': item['quantity'],
                'selected_size': item.get('size', ''),
                'selected_color': item.get('color', ''),
                'final_price': price,
                'subtotal': price * item['quantity']
            }
            cart_products.append(cart_product)
            total += cart_product['subtotal']
    
    return render_template('cart.html', cart_items=cart_products, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    size = request.form.get('size', '')
    color = request.form.get('color', '')
    
    cart = session.get('cart', [])
    
    # Check if same product with same size and color exists
    existing_item = next((item for item in cart 
                         if item['product_id'] == product_id 
                         and item.get('size') == size 
                         and item.get('color') == color), None)
    
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        cart.append({
            'product_id': product_id, 
            'quantity': quantity,
            'size': size,
            'color': color
        })
    
    session['cart'] = cart
    flash('محصول به سبد خرید اضافه شد!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', [])
    
    for item in cart:
        if item['product_id'] == product_id:
            if quantity > 0:
                item['quantity'] = quantity
            else:
                cart.remove(item)
            break
    
    session['cart'] = cart
    flash('سبد خرید بروزرسانی شد!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    flash('محصول از سبد خرید حذف شد.', 'info')
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    flash('سبد خرید خالی شد.', 'info')
    return redirect(url_for('cart'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        users = load_users()
        user = next((u for u in users if u['email'] == email), None)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', False)
            flash(f'خوش آمدید، {user["username"]}!', 'success')
            
            if user.get('is_admin'):
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('ایمیل یا رمز عبور اشتباه است.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('رمز عبور و تکرار آن مطابقت ندارند.', 'danger')
            return render_template('register.html')
        
        users = load_users()
        
        if any(u['email'] == email for u in users):
            flash('این ایمیل قبلاً ثبت شده است.', 'danger')
            return render_template('register.html')
        
        if any(u['username'] == username for u in users):
            flash('این نام کاربری قبلاً انتخاب شده است.', 'danger')
            return render_template('register.html')
        
        new_user = {
            'id': max([u['id'] for u in users], default=0) + 1,
            'username': username,
            'email': email,
            'phone': phone,
            'password': generate_password_hash(password),
            'is_admin': False,
            'created_at': get_jalali_datetime()
        }
        
        users.append(new_user)
        save_users(users)
        
        flash('ثبت نام با موفقیت انجام شد! لطفاً وارد شوید.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('با موفقیت خارج شدید.', 'info')
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    products = load_products()
    users = load_users()
    
    # Count statistics
    total_products = len(products)
    total_users = len([u for u in users if not u.get('is_admin')])
    discounted_products = len([p for p in products if is_discount_active(p)])
    
    return render_template('admin_dashboard.html', 
                         products=products, 
                         users=users,
                         total_products=total_products,
                         total_users=total_users,
                         discounted_products=discounted_products)

@app.route('/admin/products')
@admin_required
def admin_products():
    products = load_products()
    return render_template('admin_products.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        products = load_products()
        
        # Get sizes and colors as lists
        sizes = request.form.getlist('sizes[]')
        colors = request.form.getlist('colors[]')
        
        # Handle discount
        has_discount = request.form.get('has_discount') == 'on'
        discount_percent = 0
        discount_start = ''
        discount_end = ''
        
        if has_discount:
            discount_percent = int(request.form.get('discount_percent', 0))
            discount_start = request.form.get('discount_start', '')
            discount_end = request.form.get('discount_end', '')
        
        new_product = {
            'id': max([p['id'] for p in products], default=0) + 1,
            'name': request.form.get('name'),
            'price': int(request.form.get('price')),
            'category': request.form.get('category'),
            'age_group': request.form.get('age_group'),
            'sizes': sizes,
            'colors': colors,
            'description': request.form.get('description'),
            'image': request.form.get('image'),
            'stock': int(request.form.get('stock', 0)),
            'has_discount': has_discount,
            'discount_percent': discount_percent,
            'discount_start': discount_start,
            'discount_end': discount_end,
            'created_at': get_jalali_date()
        }
        
        products.append(new_product)
        save_products(products)
        
        flash('محصول با موفقیت اضافه شد!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin_add_product.html', today=get_jalali_date())

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        flash('محصول یافت نشد.', 'danger')
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        # Get sizes and colors as lists
        sizes = request.form.getlist('sizes[]')
        colors = request.form.getlist('colors[]')
        
        # Handle discount
        has_discount = request.form.get('has_discount') == 'on'
        discount_percent = 0
        discount_start = ''
        discount_end = ''
        
        if has_discount:
            discount_percent = int(request.form.get('discount_percent', 0))
            discount_start = request.form.get('discount_start', '')
            discount_end = request.form.get('discount_end', '')
        
        product['name'] = request.form.get('name')
        product['price'] = int(request.form.get('price'))
        product['category'] = request.form.get('category')
        product['age_group'] = request.form.get('age_group')
        product['sizes'] = sizes
        product['colors'] = colors
        product['description'] = request.form.get('description')
        product['image'] = request.form.get('image')
        product['stock'] = int(request.form.get('stock', 0))
        product['has_discount'] = has_discount
        product['discount_percent'] = discount_percent
        product['discount_start'] = discount_start
        product['discount_end'] = discount_end
        
        save_products(products)
        flash('محصول با موفقیت ویرایش شد!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin_add_product.html', product=product, editing=True, today=get_jalali_date())

@app.route('/admin/delete_product/<int:product_id>')
@admin_required
def admin_delete_product(product_id):
    products = load_products()
    products = [p for p in products if p['id'] != product_id]
    save_products(products)
    flash('محصول با موفقیت حذف شد!', 'success')
    return redirect(url_for('admin_products'))

# User management routes
@app.route('/admin/users')
@admin_required
def admin_users():
    users = load_users()
    # Filter out admin from the list (optional)
    regular_users = [u for u in users if not u.get('is_admin')]
    return render_template('admin_users.html', users=regular_users)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        flash('کاربر یافت نشد.', 'danger')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_phone = request.form.get('phone')
        new_password = request.form.get('password')
        
        # Check for duplicate email (excluding current user)
        if any(u['email'] == new_email and u['id'] != user_id for u in users):
            flash('این ایمیل قبلاً ثبت شده است.', 'danger')
            return render_template('admin_edit_user.html', user=user)
        
        user['username'] = new_username
        user['email'] = new_email
        user['phone'] = new_phone
        
        if new_password:
            user['password'] = generate_password_hash(new_password)
        
        save_users(users)
        flash('اطلاعات کاربر با موفقیت ویرایش شد!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin_edit_user.html', user=user)

@app.route('/admin/delete_user/<int:user_id>')
@admin_required
def admin_delete_user(user_id):
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)
    
    if user and user.get('is_admin'):
        flash('امکان حذف حساب ادمین وجود ندارد.', 'danger')
        return redirect(url_for('admin_users'))
    
    users = [u for u in users if u['id'] != user_id]
    save_users(users)
    flash('کاربر با موفقیت حذف شد!', 'success')
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    app.run(debug=True)