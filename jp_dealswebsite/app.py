import os
import sqlite3
import time
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify, flash, session
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Detect if running on Vercel
# Vercel sets VERCEL=1, but also check for other indicators
IS_VERCEL = os.environ.get('VERCEL', '0') == '1' or os.environ.get('VERCEL_ENV') is not None

# Initialize Flask app with explicit template and static folders
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# For Vercel, use /tmp for database and uploads (ephemeral storage)
# NOTE: Data will not persist between deployments on Vercel
# Consider using a cloud database (PostgreSQL, MySQL) for production
if IS_VERCEL:
    app.config['DATABASE'] = '/tmp/deals.db'
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    app.config['DATABASE'] = os.path.join(BASE_DIR, 'deals.db')
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Simple admin credentials (in production, use proper authentication)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Ensure upload directory exists (lazy initialization to avoid errors during import)
# This will be created on first use, not during import
def ensure_upload_dir():
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create upload folder: {e}")

if not IS_VERCEL:
    try:
        os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create static folder: {e}")

# Initialize database flag (for Vercel)
_db_initialized = False

def get_db():
    global _db_initialized
    # Initialize database on first request if needed (especially for Vercel)
    if not _db_initialized:
        try:
            # Ensure database directory exists
            db_dir = os.path.dirname(app.config['DATABASE'])
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Check if database exists
            if not os.path.exists(app.config['DATABASE']):
                init_db()
            else:
                # Just verify it's accessible
                test_con = sqlite3.connect(app.config['DATABASE'])
                test_con.close()
            _db_initialized = True
        except Exception as e:
            # Log error but don't fail - let the actual connection attempt handle it
            import traceback
            print(f"Warning: Database initialization error: {e}")
            print(traceback.format_exc())
    try:
        return sqlite3.connect(app.config['DATABASE'])
    except Exception as e:
        # If connection fails, try to recreate database
        try:
            if os.path.exists(app.config['DATABASE']):
                os.remove(app.config['DATABASE'])
            init_db()
            return sqlite3.connect(app.config['DATABASE'])
        except Exception as e2:
            raise Exception(f"Database connection failed: {e}, recovery failed: {e2}")

def init_db():
    try:
        # Ensure database directory exists
        db_path = app.config['DATABASE']
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        con = sqlite3.connect(db_path)
        con.execute('PRAGMA foreign_keys = ON;')
        
        # Drop and recreate tables to ensure proper schema
        con.execute("DROP TABLE IF EXISTS deal_of_the_day")
        con.execute("DROP TABLE IF EXISTS deals")
        con.execute("DROP TABLE IF EXISTS categories")
        
        con.execute("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
        con.execute("""
            CREATE TABLE deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            price REAL NOT NULL,
            original_price REAL,
            discount INTEGER,
            image_filename TEXT,
            category_id INTEGER,
            description TEXT,
            stock_quantity INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
    """)
        con.execute("""
            CREATE TABLE deal_of_the_day (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(deal_id) REFERENCES deals(id) ON DELETE CASCADE
        );
    """)
        
        # Add default categories
        default_categories = [
            ('Electronics', 'electronics'),
            ('Fashion', 'fashion'),
            ('Home & Kitchen', 'home'),
            ('Beauty', 'beauty'),
            ('Books', 'books'),
            ('Sports', 'sports')
        ]
        
        for name, slug in default_categories:
            con.execute("INSERT INTO categories(name, slug) VALUES(?, ?)", (name, slug))
        
        con.commit()
        con.close()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'con' in locals():
            con.close()
        raise

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_deal_of_the_day():
    """Get current deal of the day"""
    con = get_db()
    con.row_factory = sqlite3.Row
    today = time.strftime('%Y-%m-%d')
    
    deal = con.execute("""
        SELECT d.*, c.name AS category_name, c.slug AS category_slug
        FROM deal_of_the_day dotd
        JOIN deals d ON d.id = dotd.deal_id
        LEFT JOIN categories c ON c.id = d.category_id
        WHERE dotd.is_active = 1 
        AND (dotd.end_date IS NULL OR dotd.end_date >= ?)
        AND d.is_active = 1
        ORDER BY dotd.created_at DESC
        LIMIT 1
    """, (today,)).fetchone()
    
    con.close()
    return deal

@app.route('/')
def home():
    con = get_db()
    con.row_factory = sqlite3.Row
    
    # Get query parameters
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'newest')
    max_price = request.args.get('max_price', '')
    
    # Build base query
    base_query = """
        SELECT d.*, c.name AS category_name, c.slug AS category_slug
        FROM deals d
        LEFT JOIN categories c ON c.id = d.category_id
    """
    
    # Build WHERE conditions
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append("d.title LIKE ?")
        params.append(f"%{search}%")
    
    if max_price and max_price.isdigit():
        where_conditions.append("d.price <= ?")
        params.append(float(max_price))
    
    # Build ORDER BY clause
    order_by = "ORDER BY "
    if sort_by == 'discount':
        order_by += "d.discount DESC NULLS LAST, d.created_at DESC"
    elif sort_by == 'price-low':
        order_by += "d.price ASC, d.created_at DESC"
    elif sort_by == 'price-high':
        order_by += "d.price DESC, d.created_at DESC"
    else:  # newest
        order_by += "d.created_at DESC, d.id DESC"
    
    # Combine query
    if where_conditions:
        query = base_query + " WHERE " + " AND ".join(where_conditions) + " " + order_by
    else:
        query = base_query + " " + order_by
    
    cur = con.execute(query, params)
    deals = cur.fetchall()
    cats = con.execute("SELECT id, name, slug FROM categories ORDER BY name ASC").fetchall()
    con.close()
    
    # Get deal of the day
    deal_of_the_day = get_deal_of_the_day()
    
    return render_template('home.html', deals=deals, categories=cats, 
                         search=search, sort_by=sort_by, max_price=max_price,
                         deal_of_the_day=deal_of_the_day)

@app.route('/category/<slug>')
def category_page(slug):
    con = get_db()
    con.row_factory = sqlite3.Row
    cat = con.execute("SELECT id, name, slug FROM categories WHERE slug = ?", (slug,)).fetchone()
    if not cat:
        con.close()
        abort(404)
    
    # Get query parameters
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'newest')
    max_price = request.args.get('max_price', '')
    
    # Build base query for category
    base_query = """
        SELECT d.*, c.name AS category_name, c.slug AS category_slug
        FROM deals d
        LEFT JOIN categories c ON c.id = d.category_id
        WHERE d.category_id = ?
    """
    
    # Build WHERE conditions
    where_conditions = ["d.category_id = ?"]
    params = [cat['id']]
    
    if search:
        where_conditions.append("d.title LIKE ?")
        params.append(f"%{search}%")
    
    if max_price and max_price.isdigit():
        where_conditions.append("d.price <= ?")
        params.append(float(max_price))
    
    # Build ORDER BY clause
    order_by = "ORDER BY "
    if sort_by == 'discount':
        order_by += "d.discount DESC NULLS LAST, d.created_at DESC"
    elif sort_by == 'price-low':
        order_by += "d.price ASC, d.created_at DESC"
    elif sort_by == 'price-high':
        order_by += "d.price DESC, d.created_at DESC"
    else:  # newest
        order_by += "d.created_at DESC, d.id DESC"
    
    # Combine query
    if len(where_conditions) > 1:
        query = base_query + " AND " + " AND ".join(where_conditions[1:]) + " " + order_by
    else:
        query = base_query + " " + order_by
    
    cur = con.execute(query, params)
    deals = cur.fetchall()
    cats = con.execute("SELECT id, name, slug FROM categories ORDER BY name ASC").fetchall()
    con.close()
    
    return render_template('category.html', deals=deals, category=cat, categories=cats,
                         search=search, sort_by=sort_by, max_price=max_price)

@app.route('/api/deals')
def api_deals():
    con = get_db()
    con.row_factory = sqlite3.Row
    category = request.args.get('category', 'all')
    
    if category == 'all':
        deals = con.execute("""
            SELECT d.*, c.name AS category_name, c.slug AS category_slug
            FROM deals d
            LEFT JOIN categories c ON c.id = d.category_id
            ORDER BY d.created_at DESC, d.id DESC
        """).fetchall()
    else:
        deals = con.execute("""
            SELECT d.*, c.name AS category_name, c.slug AS category_slug
            FROM deals d
            LEFT JOIN categories c ON c.id = d.category_id
            WHERE c.slug = ?
            ORDER BY d.created_at DESC, d.id DESC
        """, (category,)).fetchall()
    
    con.close()
    
    # Convert to format expected by your JavaScript
    deals_list = []
    for deal in deals:
        deals_list.append({
            'id': deal['id'],
            'title': deal['title'],
            'price': deal['price'],
            'originalPrice': deal['original_price'] or deal['price'],
            'discount': deal['discount'] or 0,
            'image': f"/static/uploads/{deal['image_filename']}" if deal['image_filename'] else "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            'category': deal['category_slug'] or 'electronics',
            'affiliate': deal['url']
        })
    
    return jsonify(deals_list)

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_redirect():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    try:
        con = get_db()
        con.row_factory = sqlite3.Row
        
        if request.method == 'POST':
            form_type = request.form.get('form_type')
            
            if form_type == 'category':
                name = request.form.get('name')
                slug = request.form.get('slug')
                try:
                    con.execute("INSERT INTO categories(name, slug) VALUES(?, ?)", (name, slug))
                    con.commit()
                    flash('Category added successfully!', 'success')
                except sqlite3.IntegrityError:
                    flash('Category already exists!', 'error')
            
            elif form_type == 'deal':
                title = request.form.get('title')
                url = request.form.get('url')
                price = float(request.form.get('price'))
                original_price = request.form.get('original_price')
                original_price = float(original_price) if original_price else None
                category_id = request.form.get('category_id')
                category_id = int(category_id) if category_id else None
                
                # Calculate discount if original price is provided
                discount = None
                if original_price and original_price > price:
                    discount = int(((original_price - price) / original_price) * 100)
                
                # Handle image upload
                image_filename = None
                if 'image' in request.files:
                    file = request.files['image']
                    if file and file.filename and allowed_file(file.filename):
                        ensure_upload_dir()  # Ensure directory exists
                        filename = secure_filename(file.filename)
                        # Add timestamp to make filename unique
                        name, ext = os.path.splitext(filename)
                        image_filename = f"{name}_{int(time.time())}{ext}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                
                try:
                    con.execute("""
                        INSERT INTO deals (title, url, price, original_price, discount, image_filename, category_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (title, url, price, original_price, discount, image_filename, category_id))
                    con.commit()
                    flash('Deal added successfully!', 'success')
                except Exception as e:
                    flash(f'Error adding deal: {str(e)}', 'error')
        
        # Get all categories and deals for display
        categories = con.execute("SELECT id, name, slug FROM categories ORDER BY name ASC").fetchall()
        deals = con.execute("""
            SELECT d.*, c.name AS category_name 
            FROM deals d 
            LEFT JOIN categories c ON c.id = d.category_id 
            ORDER BY d.created_at DESC 
            LIMIT 20
        """).fetchall()
        
        con.close()
        return render_template('admin1.html', categories=categories, deals=deals)
    except Exception as e:
        return f"Error: {e}", 500

# Category CRUD Routes
@app.route('/admin/categories')
@admin_required
def admin_categories():
    con = get_db()
    con.row_factory = sqlite3.Row
    
    # Get categories with product counts
    categories = con.execute("""
        SELECT c.*, COUNT(d.id) as product_count
        FROM categories c
        LEFT JOIN deals d ON d.category_id = c.id AND d.is_active = 1
        GROUP BY c.id
        ORDER BY c.name ASC
    """).fetchall()
    
    con.close()
    return render_template('admin_categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description', '')
        
        try:
            con = get_db()
            con.execute("INSERT INTO categories(name, slug, description) VALUES(?, ?, ?)", 
                       (name, slug, description))
            con.commit()
            con.close()
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin_categories'))
        except sqlite3.IntegrityError:
            flash('Category already exists!', 'error')
    
    return render_template('admin_add_category.html')

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(category_id):
    con = get_db()
    con.row_factory = sqlite3.Row
    
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description', '')
        
        try:
            con.execute("UPDATE categories SET name=?, slug=?, description=? WHERE id=?", 
                       (name, slug, description, category_id))
            con.commit()
            con.close()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin_categories'))
        except sqlite3.IntegrityError:
            flash('Category already exists!', 'error')
    
    category = con.execute("SELECT * FROM categories WHERE id=?", (category_id,)).fetchone()
    con.close()
    
    if not category:
        flash('Category not found!', 'error')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin_edit_category.html', category=category)

@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    try:
        con = get_db()
        # Check if category has products
        product_count = con.execute("SELECT COUNT(*) FROM deals WHERE category_id=?", (category_id,)).fetchone()[0]
        
        if product_count > 0:
            flash(f'Cannot delete category with {product_count} products!', 'error')
        else:
            con.execute("DELETE FROM categories WHERE id=?", (category_id,))
            con.commit()
            flash('Category deleted successfully!', 'success')
        
        con.close()
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'error')
    
    return redirect(url_for('admin_categories'))

# Product CRUD Routes
@app.route('/admin/products')
@admin_required
def admin_products():
    con = get_db()
    con.row_factory = sqlite3.Row
    
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    query = """
        SELECT d.*, c.name AS category_name
        FROM deals d
        LEFT JOIN categories c ON c.id = d.category_id
        WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND d.title LIKE ?"
        params.append(f"%{search}%")
    
    if category_filter:
        query += " AND d.category_id = ?"
        params.append(category_filter)
    
    query += " ORDER BY d.created_at DESC"
    
    products = con.execute(query, params).fetchall()
    categories = con.execute("SELECT id, name FROM categories ORDER BY name ASC").fetchall()
    con.close()
    
    return render_template('admin_products.html', products=products, categories=categories, 
                         search=search, category_filter=category_filter)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    con = get_db()
    con.row_factory = sqlite3.Row
    
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        price = float(request.form.get('price'))
        original_price = request.form.get('original_price')
        original_price = float(original_price) if original_price else None
        category_id = request.form.get('category_id')
        category_id = int(category_id) if category_id else None
        description = request.form.get('description', '')
        stock_quantity = int(request.form.get('stock_quantity', 0))
        
        # Calculate discount
        discount = None
        if original_price and original_price > price:
            discount = int(((original_price - price) / original_price) * 100)
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                image_filename = f"{name}_{int(time.time())}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        try:
            con.execute("""
                INSERT INTO deals (title, url, price, original_price, discount, image_filename, 
                                 category_id, description, stock_quantity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, url, price, original_price, discount, image_filename, 
                  category_id, description, stock_quantity))
            con.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'error')
    
    categories = con.execute("SELECT id, name FROM categories ORDER BY name ASC").fetchall()
    con.close()
    
    return render_template('admin_add_product.html', categories=categories)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    con = get_db()
    con.row_factory = sqlite3.Row
    
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        price = float(request.form.get('price'))
        original_price = request.form.get('original_price')
        original_price = float(original_price) if original_price else None
        category_id = request.form.get('category_id')
        category_id = int(category_id) if category_id else None
        description = request.form.get('description', '')
        stock_quantity = int(request.form.get('stock_quantity', 0))
        is_active = bool(request.form.get('is_active'))
        
        # Calculate discount
        discount = None
        if original_price and original_price > price:
            discount = int(((original_price - price) / original_price) * 100)
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                image_filename = f"{name}_{int(time.time())}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        try:
            if image_filename:
                con.execute("""
                    UPDATE deals SET title=?, url=?, price=?, original_price=?, discount=?, 
                                   image_filename=?, category_id=?, description=?, stock_quantity=?, 
                                   is_active=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (title, url, price, original_price, discount, image_filename, 
                      category_id, description, stock_quantity, is_active, product_id))
            else:
                con.execute("""
                    UPDATE deals SET title=?, url=?, price=?, original_price=?, discount=?, 
                                   category_id=?, description=?, stock_quantity=?, 
                                   is_active=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (title, url, price, original_price, discount, 
                      category_id, description, stock_quantity, is_active, product_id))
            
            con.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            flash(f'Error updating product: {str(e)}', 'error')
    
    product = con.execute("SELECT * FROM deals WHERE id=?", (product_id,)).fetchone()
    categories = con.execute("SELECT id, name FROM categories ORDER BY name ASC").fetchall()
    con.close()
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('admin_products'))
    
    return render_template('admin_edit_product.html', product=product, categories=categories)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    try:
        con = get_db()
        con.execute("DELETE FROM deals WHERE id=?", (product_id,))
        con.commit()
        con.close()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('admin_products'))

# Deal of the Day Management
@app.route('/admin/deals-of-the-day')
@admin_required
def admin_deals_of_the_day():
    con = get_db()
    con.row_factory = sqlite3.Row
    
    deals = con.execute("""
        SELECT dotd.*, d.title, d.price, d.original_price, d.discount, d.image_filename,
               c.name AS category_name
        FROM deal_of_the_day dotd
        JOIN deals d ON d.id = dotd.deal_id
        LEFT JOIN categories c ON c.id = d.category_id
        ORDER BY dotd.created_at DESC
    """).fetchall()
    
    con.close()
    return render_template('admin_deals_of_the_day.html', deals=deals)

@app.route('/admin/deals-of-the-day/add', methods=['GET', 'POST'])
@admin_required
def admin_add_deal_of_the_day():
    con = get_db()
    con.row_factory = sqlite3.Row
    
    if request.method == 'POST':
        deal_id = request.form.get('deal_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') or None
        
        try:
            con.execute("""
                INSERT INTO deal_of_the_day (deal_id, start_date, end_date)
                VALUES (?, ?, ?)
            """, (deal_id, start_date, end_date))
            con.commit()
            flash('Deal of the Day added successfully!', 'success')
            return redirect(url_for('admin_deals_of_the_day'))
        except Exception as e:
            flash(f'Error adding deal: {str(e)}', 'error')
    
    # Get active products
    products = con.execute("""
        SELECT d.*, c.name AS category_name
        FROM deals d
        LEFT JOIN categories c ON c.id = d.category_id
        WHERE d.is_active = 1
        ORDER BY d.title ASC
    """).fetchall()
    
    con.close()
    return render_template('admin_add_deal_of_the_day.html', products=products)

@app.route('/admin/deals-of-the-day/delete/<int:deal_id>', methods=['POST'])
@admin_required
def admin_delete_deal_of_the_day(deal_id):
    try:
        con = get_db()
        con.execute("DELETE FROM deal_of_the_day WHERE id=?", (deal_id,))
        con.commit()
        con.close()
        flash('Deal of the Day deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting deal: {str(e)}', 'error')
    
    return redirect(url_for('admin_deals_of_the_day'))

@app.route('/add-sample-deals')
def add_sample_deals():
    con = get_db()
    try:
        # Add some sample deals for testing
        sample_deals = [
            ('Apple iPhone 15 Pro Max (256GB)', 'https://amazon.in/dp/iphone15', 129999, 159999, 1),
            ('Nike Air Max Running Shoes', 'https://amazon.in/dp/nike-airmax', 4999, 9999, 2),
            ('Smart LED TV 55 inch 4K', 'https://amazon.in/dp/smart-tv', 34999, 69999, 1),
            ('Instant Pot 6 Qt Pressure Cooker', 'https://amazon.in/dp/instant-pot', 7499, 12999, 3),
            ('Lakme Makeup Kit - Complete Set', 'https://amazon.in/dp/lakme-kit', 1299, 2999, 4),
            ('Atomic Habits by James Clear', 'https://amazon.in/dp/atomic-habits', 399, 599, 5),
            ('Yoga Mat Anti-Skid with Bag', 'https://amazon.in/dp/yoga-mat', 799, 1999, 6),
            ('Levi\'s Men\'s Slim Fit Jeans', 'https://amazon.in/dp/levis-jeans', 1899, 3999, 2),
            ('Sony WH-1000XM5 Headphones', 'https://amazon.in/dp/sony-headphones', 24999, 29999, 1),
            ('Stainless Steel Cookware Set (7 Pcs)', 'https://amazon.in/dp/cookware-set', 4999, 9999, 3)
        ]
        
        for title, url, price, original_price, category_id in sample_deals:
            discount = int(((original_price - price) / original_price) * 100) if original_price > price else None
            con.execute("""
                INSERT OR IGNORE INTO deals (title, url, price, original_price, discount, category_id, description, stock_quantity, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, url, price, original_price, discount, category_id, f"Great deal on {title}", 100, 1))
        
        con.commit()
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        return f"Error adding sample deals: {e}", 500
    finally:
        con.close()

if __name__ == '__main__':
    # Only initialize database on local run, not on Vercel
    if not IS_VERCEL:
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)