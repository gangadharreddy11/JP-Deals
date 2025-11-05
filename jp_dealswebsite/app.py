import os
import time
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, jsonify, flash, session
from werkzeug.utils import secure_filename
from jp_dealswebsite.database import get_db, init_db, return_db_connection

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Detect if running on Vercel
# Vercel sets VERCEL=1, but also check for other indicators
IS_VERCEL = os.environ.get('VERCEL', '0') == '1' or os.environ.get('VERCEL_ENV') is not None

# Initialize Flask app with explicit template and static folders
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'),
            static_url_path='/static')

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Use Supabase Storage for uploads (or local for development)
# For Supabase Storage, we'll use the Supabase client
if IS_VERCEL:
    # Use Supabase Storage bucket for uploads
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'  # Temporary until we implement Supabase Storage
else:
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

# Ensure static directory exists (for both local and Vercel)
# Make this lazy to avoid errors during import
def ensure_static_dirs():
    try:
        static_dir = os.path.join(BASE_DIR, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, exist_ok=True)
        # Ensure static/uploads exists for uploads route
        uploads_dir = os.path.join(static_dir, 'uploads')
        if not os.path.exists(uploads_dir) and not IS_VERCEL:
            os.makedirs(uploads_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create static folder: {e}")

# Only create static dirs on Vercel if they don't exist (avoid errors)
if IS_VERCEL:
    try:
        static_dir = os.path.join(BASE_DIR, 'static')
        if not os.path.exists(static_dir):
            # On Vercel, static files should already be deployed
            # Just ensure we don't crash if they don't exist
            pass
    except:
        pass
else:
    ensure_static_dirs()

# Initialize database flag (for Supabase)
_db_initialized = False

def ensure_db_initialized():
    """Ensure database is initialized (lazy initialization)"""
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            _db_initialized = True
        except Exception as e:
            # If tables already exist, that's fine
            error_msg = str(e).lower()
            if 'already exists' in error_msg or 'duplicate' in error_msg:
                _db_initialized = True
            else:
                # Log but don't fail - let the actual query handle it
                print(f"Warning: Database initialization: {e}")
                _db_initialized = True

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
    try:
        ensure_db_initialized()
        conn, cur = get_db()
        
        try:
            today = time.strftime('%Y-%m-%d')
            
            cur.execute("""
                SELECT d.*, c.name AS category_name, c.slug AS category_slug
                FROM deal_of_the_day dotd
                JOIN deals d ON d.id = dotd.deal_id
                LEFT JOIN categories c ON c.id = d.category_id
                WHERE dotd.is_active = true 
                AND (dotd.end_date IS NULL OR dotd.end_date >= %s)
                AND d.is_active = true
                ORDER BY dotd.created_at DESC
                LIMIT 1
            """, (today,))
            
            deal = cur.fetchone()
            return deal
        finally:
            cur.close()
            return_db_connection(conn)
    except Exception as e:
        print(f"Error getting deal of the day: {e}")
        return None

@app.route('/')
def home():
    try:
        ensure_db_initialized()
        conn, cur = get_db()
        
        try:
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
                where_conditions.append("d.title LIKE %s")
                params.append(f"%{search}%")
            
            if max_price and max_price.isdigit():
                where_conditions.append("d.price <= %s")
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
            
            cur.execute(query, params)
            deals = cur.fetchall()
            cur.execute("SELECT id, name, slug FROM categories ORDER BY name ASC")
            cats = cur.fetchall()
            
            # Get deal of the day
            deal_of_the_day = get_deal_of_the_day()
            
            return render_template('home.html', deals=deals, categories=cats, 
                                 search=search, sort_by=sort_by, max_price=max_price,
                                 deal_of_the_day=deal_of_the_day)
        finally:
            cur.close()
            return_db_connection(conn)
    except Exception as e:
        error_msg = str(e)
        if 'DATABASE_URL' in error_msg:
            return f'''
            <html>
            <head><title>Configuration Error</title></head>
            <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: 0 auto;">
                <h1>⚠️ Database Configuration Required</h1>
                <p>The <code>DATABASE_URL</code> environment variable is not set.</p>
                <h2>How to Fix:</h2>
                <ol>
                    <li>Go to your <strong>Supabase Dashboard</strong></li>
                    <li>Navigate to <strong>Settings → Database</strong></li>
                    <li>Copy the <strong>Connection string (URI)</strong></li>
                    <li>Go to <strong>Vercel Dashboard → Your Project → Settings → Environment Variables</strong></li>
                    <li>Add a new variable: <code>DATABASE_URL</code> with your connection string</li>
                    <li>Redeploy your application</li>
                </ol>
                <p><strong>Error Details:</strong></p>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_msg}</pre>
            </body>
            </html>
            ''', 500
        else:
            return f'''
            <html>
            <head><title>Database Error</title></head>
            <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: 0 auto;">
                <h1>Database Connection Error</h1>
                <p>There was an error connecting to the database:</p>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_msg}</pre>
                <p>Please check your DATABASE_URL configuration in Vercel.</p>
            </body>
            </html>
            ''', 500

@app.route('/category/<slug>')
def category_page(slug):
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        cur.execute("SELECT id, name, slug FROM categories WHERE slug = %s", (slug,))
        cat = cur.fetchone()
        if not cat:
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
            WHERE d.category_id = %s
        """
        
        # Build WHERE conditions
        where_conditions = ["d.category_id = %s"]
        params = [cat['id']]
        
        if search:
            where_conditions.append("d.title LIKE %s")
            params.append(f"%{search}%")
        
        if max_price and max_price.isdigit():
            where_conditions.append("d.price <= %s")
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
        
        cur.execute(query, params)
        deals = cur.fetchall()
        cur.execute("SELECT id, name, slug FROM categories ORDER BY name ASC")
        cats = cur.fetchall()
        
        return render_template('category.html', deals=deals, category=cat, categories=cats,
                             search=search, sort_by=sort_by, max_price=max_price)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/api/deals')
def api_deals():
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        category = request.args.get('category', 'all')
        
        if category == 'all':
            cur.execute("""
                SELECT d.*, c.name AS category_name, c.slug AS category_slug
                FROM deals d
                LEFT JOIN categories c ON c.id = d.category_id
                ORDER BY d.created_at DESC, d.id DESC
            """)
        else:
            cur.execute("""
                SELECT d.*, c.name AS category_name, c.slug AS category_slug
                FROM deals d
                LEFT JOIN categories c ON c.id = d.category_id
                WHERE c.slug = %s
                ORDER BY d.created_at DESC, d.id DESC
            """, (category,))
        
        deals = cur.fetchall()
        
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
    finally:
        cur.close()
        return_db_connection(conn)

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
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        if request.method == 'POST':
            form_type = request.form.get('form_type')
            
            if form_type == 'category':
                name = request.form.get('name')
                slug = request.form.get('slug')
                try:
                    cur.execute("INSERT INTO categories(name, slug) VALUES(%s, %s)", (name, slug))
                    conn.commit()
                    flash('Category added successfully!', 'success')
                except Exception as e:
                    if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                        flash('Category already exists!', 'error')
                    else:
                        flash(f'Error: {str(e)}', 'error')
            
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
                    cur.execute("""
                        INSERT INTO deals (title, url, price, original_price, discount, image_filename, category_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (title, url, price, original_price, discount, image_filename, category_id))
                    conn.commit()
                    flash('Deal added successfully!', 'success')
                except Exception as e:
                    flash(f'Error adding deal: {str(e)}', 'error')
        
        # Get all categories and deals for display
        cur.execute("SELECT id, name, slug FROM categories ORDER BY name ASC")
        categories = cur.fetchall()
        cur.execute("""
            SELECT d.*, c.name AS category_name 
            FROM deals d 
            LEFT JOIN categories c ON c.id = d.category_id 
            ORDER BY d.created_at DESC 
            LIMIT 20
        """)
        deals = cur.fetchall()
        
        return render_template('admin1.html', categories=categories, deals=deals)
    except Exception as e:
        return f"Error: {e}", 500
    finally:
        cur.close()
        return_db_connection(conn)

# Category CRUD Routes
@app.route('/admin/categories')
@admin_required
def admin_categories():
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        # Get categories with product counts
        cur.execute("""
            SELECT c.*, COUNT(d.id) as product_count
            FROM categories c
            LEFT JOIN deals d ON d.category_id = c.id AND d.is_active = true
            GROUP BY c.id
            ORDER BY c.name ASC
        """)
        categories = cur.fetchall()
        return render_template('admin_categories.html', categories=categories)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description', '')
        
        ensure_db_initialized()
        conn, cur = get_db()
        try:
            cur.execute("INSERT INTO categories(name, slug, description) VALUES(%s, %s, %s)", 
                       (name, slug, description))
            conn.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin_categories'))
        except Exception as e:
            if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                flash('Category already exists!', 'error')
            else:
                flash(f'Error: {str(e)}', 'error')
        finally:
            cur.close()
            return_db_connection(conn)
    
    return render_template('admin_add_category.html')

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(category_id):
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            slug = request.form.get('slug')
            description = request.form.get('description', '')
            
            try:
                cur.execute("UPDATE categories SET name=%s, slug=%s, description=%s WHERE id=%s", 
                           (name, slug, description, category_id))
                conn.commit()
                flash('Category updated successfully!', 'success')
                return redirect(url_for('admin_categories'))
            except Exception as e:
                if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                    flash('Category already exists!', 'error')
                else:
                    flash(f'Error: {str(e)}', 'error')
        
        cur.execute("SELECT * FROM categories WHERE id=%s", (category_id,))
        category = cur.fetchone()
        
        if not category:
            flash('Category not found!', 'error')
            return redirect(url_for('admin_categories'))
        
        return render_template('admin_edit_category.html', category=category)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        # Check if category has products
        cur.execute("SELECT COUNT(*) FROM deals WHERE category_id=%s", (category_id,))
        product_count = cur.fetchone()['count']
        
        if product_count > 0:
            flash(f'Cannot delete category with {product_count} products!', 'error')
        else:
            cur.execute("DELETE FROM categories WHERE id=%s", (category_id,))
            conn.commit()
            flash('Category deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'error')
    finally:
        cur.close()
        return_db_connection(conn)
    
    return redirect(url_for('admin_categories'))

# Product CRUD Routes
@app.route('/admin/products')
@admin_required
def admin_products():
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
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
            query += " AND d.title LIKE %s"
            params.append(f"%{search}%")
        
        if category_filter:
            query += " AND d.category_id = %s"
            params.append(category_filter)
        
        query += " ORDER BY d.created_at DESC"
        
        cur.execute(query, params)
        products = cur.fetchall()
        cur.execute("SELECT id, name FROM categories ORDER BY name ASC")
        categories = cur.fetchall()
        
        return render_template('admin_products.html', products=products, categories=categories, 
                             search=search, category_filter=category_filter)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
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
                    ensure_upload_dir()
                    filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(filename)
                    image_filename = f"{name}_{int(time.time())}{ext}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            
            try:
                cur.execute("""
                    INSERT INTO deals (title, url, price, original_price, discount, image_filename, 
                                     category_id, description, stock_quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, url, price, original_price, discount, image_filename, 
                      category_id, description, stock_quantity))
                conn.commit()
                flash('Product added successfully!', 'success')
                return redirect(url_for('admin_products'))
            except Exception as e:
                flash(f'Error adding product: {str(e)}', 'error')
        
        cur.execute("SELECT id, name FROM categories ORDER BY name ASC")
        categories = cur.fetchall()
        return render_template('admin_add_product.html', categories=categories)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
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
                    ensure_upload_dir()
                    filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(filename)
                    image_filename = f"{name}_{int(time.time())}{ext}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            
            try:
                if image_filename:
                    cur.execute("""
                        UPDATE deals SET title=%s, url=%s, price=%s, original_price=%s, discount=%s, 
                                       image_filename=%s, category_id=%s, description=%s, stock_quantity=%s, 
                                       is_active=%s, updated_at=CURRENT_TIMESTAMP
                        WHERE id=%s
                    """, (title, url, price, original_price, discount, image_filename, 
                          category_id, description, stock_quantity, is_active, product_id))
                else:
                    cur.execute("""
                        UPDATE deals SET title=%s, url=%s, price=%s, original_price=%s, discount=%s, 
                                       category_id=%s, description=%s, stock_quantity=%s, 
                                       is_active=%s, updated_at=CURRENT_TIMESTAMP
                        WHERE id=%s
                    """, (title, url, price, original_price, discount, 
                          category_id, description, stock_quantity, is_active, product_id))
                
                conn.commit()
                flash('Product updated successfully!', 'success')
                return redirect(url_for('admin_products'))
            except Exception as e:
                flash(f'Error updating product: {str(e)}', 'error')
        
        cur.execute("SELECT * FROM deals WHERE id=%s", (product_id,))
        product = cur.fetchone()
        cur.execute("SELECT id, name FROM categories ORDER BY name ASC")
        categories = cur.fetchall()
        
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('admin_products'))
        
        return render_template('admin_edit_product.html', product=product, categories=categories)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        cur.execute("DELETE FROM deals WHERE id=%s", (product_id,))
        conn.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    finally:
        cur.close()
        return_db_connection(conn)
    
    return redirect(url_for('admin_products'))

# Deal of the Day Management
@app.route('/admin/deals-of-the-day')
@admin_required
def admin_deals_of_the_day():
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        cur.execute("""
            SELECT dotd.*, d.title, d.price, d.original_price, d.discount, d.image_filename,
                   c.name AS category_name
            FROM deal_of_the_day dotd
            JOIN deals d ON d.id = dotd.deal_id
            LEFT JOIN categories c ON c.id = d.category_id
            ORDER BY dotd.created_at DESC
        """)
        deals = cur.fetchall()
        return render_template('admin_deals_of_the_day.html', deals=deals)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/admin/deals-of-the-day/add', methods=['GET', 'POST'])
@admin_required
def admin_add_deal_of_the_day():
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        if request.method == 'POST':
            deal_id = request.form.get('deal_id')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date') or None
            
            try:
                cur.execute("""
                    INSERT INTO deal_of_the_day (deal_id, start_date, end_date)
                    VALUES (%s, %s, %s)
                """, (deal_id, start_date, end_date))
                conn.commit()
                flash('Deal of the Day added successfully!', 'success')
                return redirect(url_for('admin_deals_of_the_day'))
            except Exception as e:
                flash(f'Error adding deal: {str(e)}', 'error')
        
        # Get active products
        cur.execute("""
            SELECT d.*, c.name AS category_name
            FROM deals d
            LEFT JOIN categories c ON c.id = d.category_id
            WHERE d.is_active = true
            ORDER BY d.title ASC
        """)
        products = cur.fetchall()
        return render_template('admin_add_deal_of_the_day.html', products=products)
    finally:
        cur.close()
        return_db_connection(conn)

@app.route('/admin/deals-of-the-day/delete/<int:deal_id>', methods=['POST'])
@admin_required
def admin_delete_deal_of_the_day(deal_id):
    ensure_db_initialized()
    conn, cur = get_db()
    
    try:
        cur.execute("DELETE FROM deal_of_the_day WHERE id=%s", (deal_id,))
        conn.commit()
        flash('Deal of the Day deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting deal: {str(e)}', 'error')
    finally:
        cur.close()
        return_db_connection(conn)
    
    return redirect(url_for('admin_deals_of_the_day'))

@app.route('/add-sample-deals')
def add_sample_deals():
    ensure_db_initialized()
    conn, cur = get_db()
    
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
            cur.execute("""
                INSERT INTO deals (title, url, price, original_price, discount, category_id, description, stock_quantity, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (title, url, price, original_price, discount, category_id, f"Great deal on {title}", 100, True))
        
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        return f"Error adding sample deals: {e}", 500
    finally:
        cur.close()
        return_db_connection(conn)

if __name__ == '__main__':
    # Only initialize database on local run, not on Vercel
    if not IS_VERCEL:
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)