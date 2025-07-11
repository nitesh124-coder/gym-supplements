from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'gym_supplements_nutrition_product_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_supplements_nutrition_product.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    discounted_price = db.Column(db.Float)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0)
    stock = db.Column(db.Integer, default=0)
    type = db.Column(db.String(50))
    brand = db.Column(db.String(100))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('wishlist_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('wishlist_items', lazy=True))

# Helper function to get cart count
def get_cart_count():
    """Get the total number of items in the cart"""
    if 'user_id' in session:
        # User is logged in, get count from database
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        return sum(item.quantity for item in cart_items)
    else:
        # User is not logged in, get count from session
        if 'cart' in session and session['cart']:
            return sum(session['cart'].values())
        return 0

# Helper function to get wishlist count
def get_wishlist_count():
    """Get the total number of items in the wishlist"""
    if 'user_id' in session:
        # User is logged in, get count from database
        wishlist_items = WishlistItem.query.filter_by(user_id=session['user_id']).all()
        return len(wishlist_items)
    else:
        # User is not logged in, get count from session
        if 'wishlist' in session and session['wishlist']:
            return len(session['wishlist'])
        return 0

# Helper function to check if product is in wishlist
def is_in_wishlist(product_id):
    """Check if a product is in the user's wishlist"""
    if 'user_id' in session:
        # User is logged in, check database
        return WishlistItem.query.filter_by(user_id=session['user_id'], product_id=product_id).first() is not None
    else:
        # User is not logged in, check session
        if 'wishlist' in session and session['wishlist']:
            return str(product_id) in session['wishlist']
        return False

# Make cart_count and wishlist_count available to all templates
@app.context_processor
def inject_counts():
    return dict(
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )

# Create database with sample data if it doesn't exist
def create_sample_data():
    try:
        # Clear existing data
        db.session.query(CartItem).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Get list of actual image files
        image_dirs = {
            'whey protein': 'whey protein',
            'gainer': 'gainer',
            'preworkout': 'preworkout',
            'fatloss': 'fatloss',
            'vitmins': 'vitmins',
            'ayruveda': 'ayruveda',
            'fitfoods': 'fitfoods',
            'accessories': {
                'bottles': 'accessories/bottles',
                'bag': 'accessories/bag',
                'shoes': 'accessories/shoes',
                'heartratemonitor': 'accessories/heartratemonitor',
                'wristband': 'accessories/wristband',
                'headband': 'accessories/headband',
                'tshirt': 'accessories/tshirt',
                'caps': 'accessories/caps',
                'tracks': 'accessories/tracks',
                'shorts': 'accessories/shorts'
            }
        }

        # Dictionary to store image file lists
        image_files = {}

        # Check which directories exist and get their files
        for category, dir_name in image_dirs.items():
            if isinstance(dir_name, dict):  # Handle accessories subcategories
                image_files[category] = {}
                for subcategory, subdir in dir_name.items():
                    dir_path = os.path.join('static', 'images', subdir)
                    if os.path.exists(dir_path):
                        image_files[category][subcategory] = os.listdir(dir_path)
                        print(f"Available {subcategory} images:", image_files[category][subcategory])
                    else:
                        print(f"Warning: Directory {dir_path} does not exist")
                        image_files[category][subcategory] = []
            else:  # Handle regular categories
                dir_path = os.path.join('static', 'images', dir_name)
                if os.path.exists(dir_path):
                    image_files[category] = os.listdir(dir_path)
                    print(f"Available {category} images:", image_files[category])
                else:
                    print(f"Warning: Directory {dir_path} does not exist")
                    image_files[category] = []

        # Sample products
        products = []

        # Process each category
        for category, images in image_files.items():
            if category == 'accessories':
                # Handle accessories subcategories
                for subcategory, sub_images in images.items():
                    for img in sub_images:
                        # Skip non-image files
                        if not (img.lower().endswith('.jpg') or img.lower().endswith('.jpeg') or img.lower().endswith('.png')):
                            continue

                        # Generate product name from image name
                        product_name = img.replace('.jpg', '').replace('.jpeg', '').replace('.png', '').replace('IMG-', '').replace('WA', '').title()

                        # Category-specific pricing and descriptions
                        if subcategory == 'bottles':
                            name = f'Premium Water Bottle - {product_name}'
                            description = 'High-quality water bottle for your fitness journey'
                            price = 499
                            discounted_price = 399
                        elif subcategory == 'bag':
                            name = f'Gym Bag - {product_name}'
                            description = 'Spacious and durable gym bag with multiple compartments'
                            price = 1499
                            discounted_price = 1299
                        elif subcategory == 'shoes':
                            name = f'Training Shoes - {product_name}'
                            description = 'Comfortable and supportive training shoes'
                            price = 2499
                            discounted_price = 1999
                        elif subcategory == 'heartratemonitor':
                            name = f'Heart Rate Monitor - {product_name}'
                            description = 'Advanced heart rate monitoring device'
                            price = 1999
                            discounted_price = 1799
                        elif subcategory == 'wristband':
                            name = f'Fitness Wristband - {product_name}'
                            description = 'Stylish and functional fitness wristband'
                            price = 299
                            discounted_price = 249
                        elif subcategory == 'headband':
                            name = f'Sports Headband - {product_name}'
                            description = 'Comfortable and absorbent sports headband'
                            price = 199
                            discounted_price = 149
                        elif subcategory == 'tshirt':
                            name = f'Fitness T-Shirt - {product_name}'
                            description = 'Comfortable and breathable fitness t-shirt'
                            price = 799
                            discounted_price = 699
                        elif subcategory == 'caps':
                            name = f'Sports Cap - {product_name}'
                            description = 'Stylish and functional sports cap'
                            price = 499
                            discounted_price = 399
                        elif subcategory == 'tracks':
                            name = f'Tracksuit - {product_name}'
                            description = 'Comfortable and stylish tracksuit'
                            price = 1999
                            discounted_price = 1799
                        elif subcategory == 'shorts':
                            name = f'Training Shorts - {product_name}'
                            description = 'Comfortable and flexible training shorts'
                            price = 899
                            discounted_price = 799

                        # Verify image path exists
                        image_path = f'/static/images/accessories/{subcategory}/{img}'

                        products.append({
                            'name': name,
                            'description': description,
                            'price': price,
                            'discounted_price': discounted_price,
                            'category': 'accessories',
                            'image_url': image_path,
                            'rating': 4.5,
                            'stock': 100,
                            'type': subcategory,
                            'brand': product_name.split('-')[0].strip() if '-' in product_name else 'Unknown'
                        })
            else:
                # Handle regular categories (existing code)
                for img in images:
                    # Skip non-image files
                    if not (img.lower().endswith('.jpg') or img.lower().endswith('.jpeg') or img.lower().endswith('.png')):
                        continue

                    brand_name = img.replace('.jpg', '').replace('.jpeg', '').replace('.png', '').title()

                    # Category-specific names and descriptions
                    if category == 'whey protein':
                        name = f'{brand_name} Whey Protein'
                        description = 'Premium whey protein for muscle recovery and growth'
                        price = 2999
                        discounted_price = 2499
                    elif category == 'gainer':
                        name = f'{brand_name} Mass Gainer'
                        description = 'High calorie mass gainer for serious weight gain'
                        price = 2499
                        discounted_price = 1999
                    elif category == 'preworkout':
                        name = f'{brand_name} Pre-Workout'
                        description = 'Energy boosting pre-workout with caffeine and beta-alanine'
                        price = 1499
                        discounted_price = 1299
                    elif category == 'fatloss':
                        name = f'{brand_name} Fat Burner'
                        description = 'Advanced fat burner for accelerated weight loss'
                        price = 1299
                        discounted_price = 1099
                    elif category == 'vitmins':
                        name = f'{brand_name} Multivitamin'
                        description = 'Complete multivitamin formula for overall health'
                        price = 899
                        discounted_price = 799
                    elif category == 'ayruveda':
                        name = f'{brand_name} Ayurvedic Supplement'
                        description = 'Natural ayurvedic supplement for holistic health'
                        price = 599
                        discounted_price = 499
                    elif category == 'fitfoods':
                        name = f'{brand_name} Protein Snack'
                        description = 'High protein snack for fitness enthusiasts'
                        price = 499
                        discounted_price = 399
                    else:
                        name = f'{brand_name} Supplement'
                        description = 'Quality fitness supplement'
                        price = 999
                        discounted_price = 899

                    # Verify image path exists
                    image_path = f'/static/images/{category}/{img}'

                    products.append({
                        'name': name,
                        'description': description,
                        'price': price,
                        'discounted_price': discounted_price,
                        'category': category,
                        'image_url': image_path,
                        'rating': 4.5,
                        'stock': 100,
                        'brand': brand_name.split()[0].strip() if brand_name else 'Unknown'
                    })

        # Add all products to the database
        for product_data in products:
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                discounted_price=product_data['discounted_price'],
                category=product_data['category'],
                image_url=product_data['image_url'],
                rating=product_data['rating'],
                stock=product_data['stock'],
                type=product_data.get('type'),
                brand=product_data.get('brand')
            )
            db.session.add(product)

        # Sample user
        test_user = User(
            username='test',
            email='test@example.com',
            password='password123'  # In production, use proper password hashing
        )
        db.session.add(test_user)

        db.session.commit()
        print("Database initialized with sample data successfully")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing database: {e}")
        return False

# Initialize the database
@app.before_request
def initialize_database_if_needed():
    # Only run if we haven't set the initialization flag yet
    if not getattr(app, '_database_initialized', False):
        try:
            # Check if DB exists and has products
            product_count = Product.query.count()
            if product_count == 0:
                print("No products found in database. Initializing with sample data...")
                create_sample_data()
            else:
                print(f"Database already contains {product_count} products. No initialization needed.")

            # Set the flag to prevent re-initialization on future requests
            app._database_initialized = True
        except Exception as e:
            print(f"Error checking database: {e}")
            # Create tables if they don't exist
            db.create_all()
            # Try to initialize with sample data
            create_sample_data()
            app._database_initialized = True

# Routes
@app.route('/')
def home():
    try:
        # Featured products for the home page
        whey_products = Product.query.filter_by(category='whey protein').limit(4).all()
        gainers = Product.query.filter_by(category='gainer').limit(4).all()
        pre_workouts = Product.query.filter_by(category='preworkout').limit(4).all()

        # Create default image paths for categories if no products exist
        if not whey_products:
            print("No whey protein products found. Creating placeholder.")
            sample_whey = Product(
                name="Sample Whey Protein",
                description="Premium whey protein for muscle recovery and growth",
                price=2999,
                discounted_price=2499,
                category='whey protein',
                image_url='/static/images/placeholder.jpg',
                rating=4.5,
                stock=100
            )
            db.session.add(sample_whey)
            whey_products = [sample_whey]

        if not gainers:
            print("No mass gainer products found. Creating placeholder.")
            sample_gainer = Product(
                name="Sample Mass Gainer",
                description="High calorie mass gainer for serious weight gain",
                price=2499,
                discounted_price=1999,
                category='gainer',
                image_url='/static/images/placeholder.jpg',
                rating=4.3,
                stock=85
            )
            db.session.add(sample_gainer)
            gainers = [sample_gainer]

        if not pre_workouts:
            print("No pre-workout products found. Creating placeholder.")
            sample_preworkout = Product(
                name="Sample Pre-Workout",
                description="Energy boosting pre-workout with caffeine and beta-alanine",
                price=1499,
                discounted_price=1299,
                category='preworkout',
                image_url='/static/images/placeholder.jpg',
                rating=4.3,
                stock=110
            )
            db.session.add(sample_preworkout)
            pre_workouts = [sample_preworkout]

        db.session.commit()

        return render_template('index.html',
                          whey_products=whey_products,
                          gainers=gainers,
                          pre_workouts=pre_workouts)
    except Exception as e:
        print(f"Error in home route: {e}")
        db.session.rollback()
        return render_template('index.html',
                            whey_products=[],
                            gainers=[],
                            pre_workouts=[])

@app.route('/categories')
def categories():
    try:
        # Get all available categories with their image, color, and description
        category_data = [
            {
                'name': 'Whey Protein',
                'url': 'whey protein',
                'image': '/static/images/whey protein/dymatize.jpg',
                'color': '#FFC107',
                'description': 'High-quality protein for muscle recovery and growth'
            },
            {
                'name': 'Mass Gainers',
                'url': 'gainer',
                'image': '/static/images/gainer/serious mass.jpg',
                'color': '#28a745',
                'description': 'High-calorie supplements for weight and muscle gain'
            },
            {
                'name': 'Pre-Workout',
                'url': 'preworkout',
                'image': '/static/images/preworkout/optimum nutrition.jpg',
                'color': '#dc3545',
                'description': 'Energy and focus boosters for intense workouts'
            },
            {
                'name': 'Fat Loss',
                'url': 'fatloss',
                'image': '/static/images/fatloss/gnc.jpg',
                'color': '#17a2b8',
                'description': 'Supplements to support your weight loss journey'
            },
            {
                'name': 'Vitamins & Minerals',
                'url': 'vitmins',
                'image': '/static/images/vitmins/atom multi vitamin.jpg',
                'color': '#6f42c1',
                'description': 'Essential nutrients for overall health and wellness'
            },
            {
                'name': 'Ayurveda',
                'url': 'ayruveda',
                'image': '/static/images/ayruveda/muscle blaze ashwagandha.jpg',
                'color': '#fd7e14',
                'description': 'Natural supplements based on traditional medicine'
            },
            {
                'name': 'Fit Foods',
                'url': 'fitfoods',
                'image': '/static/images/fitfoods/muscle blaze.jpg',
                'color': '#20c997',
                'description': 'Protein-rich snacks and healthy food alternatives'
            }
        ]

        # Verify each image exists, use backup if needed
        for category in category_data:
            # First check if the directory exists
            image_path = category['image'].lstrip('/')
            directory_path = os.path.dirname(image_path)

            # Default to placeholder if problems
            default_image = '/static/images/placeholder.jpg'

            if not os.path.exists(directory_path):
                print(f"Warning: Directory {directory_path} does not exist")
                # Create the directory
                try:
                    os.makedirs(directory_path, exist_ok=True)
                    print(f"Created directory: {directory_path}")
                except Exception as e:
                    print(f"Error creating directory {directory_path}: {e}")

                category['image'] = default_image
                continue

            if not os.path.exists(image_path):
                # Try to find any image in that category folder
                if os.path.exists(directory_path) and os.listdir(directory_path):
                    # Find first image file in the directory
                    image_found = False
                    for file in os.listdir(directory_path):
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            category['image'] = f"/{directory_path}/{file}"
                            image_found = True
                            break

                    if not image_found:
                        category['image'] = default_image
                else:
                    category['image'] = default_image

        return render_template('categories.html', categories=category_data)
    except Exception as e:
        print(f"Error in categories route: {e}")
        # Return minimal functioning version with placeholder
        basic_categories = [
            {'name': 'Whey Protein', 'url': 'whey protein', 'image': '/static/images/placeholder.jpg', 'color': '#FFC107'},
            {'name': 'Mass Gainers', 'url': 'gainer', 'image': '/static/images/placeholder.jpg', 'color': '#28a745'},
            {'name': 'Pre-Workout', 'url': 'preworkout', 'image': '/static/images/placeholder.jpg', 'color': '#dc3545'}
        ]
        return render_template('categories.html', categories=basic_categories)

@app.route('/products/<category>')
def products(category):
    try:
        # Start with filtering by category
        query = Product.query.filter_by(category=category)

        # If the category is 'accessories', further filter by type if provided
        if category == 'accessories':
            selected_types = request.args.getlist('type')
            if selected_types:
                # Filter by multiple types using 'in' operator
                query = query.filter(Product.type.in_(selected_types))

        # Add price filtering
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        if min_price is not None:
            query = query.filter(Product.discounted_price >= min_price)
        if max_price is not None:
            query = query.filter(Product.discounted_price <= max_price)

        # Add brand filtering
        selected_brands = request.args.getlist('brand')
        if selected_brands:
            query = query.filter(Product.brand.in_(selected_brands))

        # Add discount filtering (e.g., ?discount=10 for 10% off or more)
        selected_discounts = request.args.getlist('discount')
        if selected_discounts:
            # Convert to float and get the minimum discount percentage
            discount_percentages = [float(d) for d in selected_discounts]
            min_discount_percentage = min(discount_percentages)

            # Calculate minimum discounted price for the given percentage
            # We need to ensure original price is not zero to avoid division by zero
            query = query.filter(
                (100 - (Product.discounted_price / Product.price * 100)) >= min_discount_percentage,
                Product.price > 0 # Avoid division by zero
            )

        products = query.all()

        # Get unique brands for the current category (or filtered products)
        # Filter out None values for brand
        available_brands = sorted(list(set([p.brand for p in Product.query.filter_by(category=category).all() if p.brand])))

        # If no products found, create a placeholder product
        if not products:
            print(f"No products found for category: {category}. Creating placeholder.")
            placeholder_product = Product(
                name=f"Sample {category.title()} Product",
                description=f"Sample description for {category}",
                price=999,
                discounted_price=799,
                category=category,
                image_url='/static/images/placeholder.jpg',
                rating=4.0,
                stock=100
            )
            db.session.add(placeholder_product)
            db.session.commit()
            products = [placeholder_product]

        return render_template('products.html', products=products, category=category, available_brands=available_brands)
    except Exception as e:
        print(f"Error in products route: {e}")
        db.session.rollback()
        return render_template('products.html', products=[], category=category, available_brands=[])

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    try:
        product = Product.query.get(product_id)

        # If product doesn't exist, redirect to categories
        if not product:
            print(f"Product with ID {product_id} not found. Redirecting to categories.")
            return redirect(url_for('categories'))

        related_products = Product.query.filter_by(category=product.category).limit(4).all()
        return render_template('product_detail.html', product=product, related_products=related_products)
    except Exception as e:
        print(f"Error in product_detail route: {e}")
        # Redirect to categories page if there's an error
        return redirect(url_for('categories'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # In production, use proper password hashing
            session['user_id'] = user.id
            return redirect(url_for('home'))

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Username already exists")

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return render_template('register.html', error="Email already registered")

        try:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            # Log in the newly registered user
            session['user_id'] = new_user.id

            # Check for items in session cart and add them to the user's cart
            if 'cart' in session and session['cart']:
                user_id = session['user_id']
                for product_id_str, quantity in session['cart'].items():
                    product_id = int(product_id_str)
                    # Check if item already in cart for this user (shouldn't happen right after registration, but good practice)
                    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
                    if cart_item:
                        cart_item.quantity += quantity
                    else:
                        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
                        db.session.add(cart_item)
                db.session.commit()
                # Clear the session cart after moving items to database
                session.pop('cart', None)

            # Check for items in session wishlist and add them to the user's wishlist
            if 'wishlist' in session and session['wishlist']:
                user_id = session['user_id']
                for product_id_str in session['wishlist']:
                    product_id = int(product_id_str)
                    # Check if item already in wishlist for this user
                    wishlist_item = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first()
                    if not wishlist_item:
                        wishlist_item = WishlistItem(user_id=user_id, product_id=product_id)
                        db.session.add(wishlist_item)
                db.session.commit()
                # Clear the session wishlist after moving items to database
                session.pop('wishlist', None)

            # Redirect based on what was transferred
            if 'cart' in session and session['cart']:
                return redirect(url_for('cart')) # Redirect to cart if items were added
            elif 'wishlist' in session and session['wishlist']:
                return redirect(url_for('wishlist')) # Redirect to wishlist if items were added

            return redirect(url_for('home')) # Redirect to home if no items in session cart

        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {e}")
            return render_template('register.html', error=f"An error occurred during registration: {e}")

    return render_template('register.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        # Redirect to login if user is not logged in
        return redirect(url_for('login'))

    user_id = session['user_id']

    # In a real application, you would save the order details to a database
    # For this simulation, we will just clear the user's cart
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # Redirect to an order confirmation page
    return redirect(url_for('order_confirmation'))

@app.route('/order_confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    cart_items = []
    total = 0

    if 'user_id' in session:
        # User is logged in, get cart from database
        cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
        total = sum(item.product.discounted_price * item.quantity for item in cart_items)
    else:
        # User is not logged in, get cart from session
        if 'cart' in session and session['cart']:
            # Create temporary cart items from session data
            cart_items = []
            for product_id_str, quantity in session['cart'].items():
                product_id = int(product_id_str)
                product = Product.query.get(product_id)
                if product:
                    # Create a temporary cart item object
                    temp_cart_item = type('CartItem', (), {
                        'product': product,
                        'quantity': quantity
                    })()
                    cart_items.append(temp_cart_item)
                    total += product.discounted_price * quantity

    # Get recommended products for the cart page
    whey_products = Product.query.filter_by(category='whey protein').limit(4).all()

    return render_template('cart.html', cart_items=cart_items, total=total, whey_products=whey_products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))

    if 'user_id' not in session:
        # Store cart item in session for unauthenticated user
        if 'cart' not in session:
            session['cart'] = {}
        # Use product_id as key, quantity as value
        # Ensure product_id is treated as string for session key
        session['cart'][str(product_id)] = session['cart'].get(str(product_id), 0) + quantity
        session.modified = True
    else:
        # If user is logged in, proceed to add to database cart
        user_id = session['user_id']

        # Check if item already in cart for this user
        cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()

    # Check if this is an AJAX request
    if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
        return jsonify({
            'success': True,
            'cart_count': get_cart_count(),
            'message': 'Product added to cart successfully!'
        })

    # Regular form submission - redirect to cart
    return redirect(url_for('cart'))

@app.route('/api/cart_count')
def api_cart_count():
    """API endpoint to get current cart count"""
    return jsonify({'cart_count': get_cart_count()})

@app.route('/api/wishlist_count')
def api_wishlist_count():
    """API endpoint to get current wishlist count"""
    return jsonify({'wishlist_count': get_wishlist_count()})

@app.route('/wishlist')
def wishlist():
    """Display user's wishlist"""
    wishlist_items = []

    if 'user_id' in session:
        # User is logged in, get wishlist from database
        wishlist_items = WishlistItem.query.filter_by(user_id=session['user_id']).all()
    else:
        # User is not logged in, get wishlist from session
        if 'wishlist' in session and session['wishlist']:
            # Create temporary wishlist items from session data
            wishlist_items = []
            for product_id_str in session['wishlist']:
                product_id = int(product_id_str)
                product = Product.query.get(product_id)
                if product:
                    # Create a temporary wishlist item object
                    temp_wishlist_item = type('WishlistItem', (), {
                        'product': product
                    })()
                    wishlist_items.append(temp_wishlist_item)

    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    """Add product to wishlist"""

    if 'user_id' not in session:
        # Store wishlist item in session for unauthenticated user
        if 'wishlist' not in session:
            session['wishlist'] = []
        # Add product_id to wishlist if not already there
        if str(product_id) not in session['wishlist']:
            session['wishlist'].append(str(product_id))
            session.modified = True
    else:
        # If user is logged in, proceed to add to database wishlist
        user_id = session['user_id']

        # Check if item already in wishlist for this user
        wishlist_item = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if not wishlist_item:
            wishlist_item = WishlistItem(user_id=user_id, product_id=product_id)
            db.session.add(wishlist_item)
            db.session.commit()

    # Check if this is an AJAX request
    if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
        return jsonify({
            'success': True,
            'wishlist_count': get_wishlist_count(),
            'message': 'Product added to wishlist successfully!'
        })

    # Regular form submission - redirect to wishlist
    return redirect(url_for('wishlist'))

@app.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""

    if 'user_id' in session:
        # User is logged in, remove from database wishlist
        user_id = session['user_id']
        wishlist_item = WishlistItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if wishlist_item:
            db.session.delete(wishlist_item)
            db.session.commit()
    else:
        # User is not logged in, remove from session wishlist
        if 'wishlist' in session and str(product_id) in session['wishlist']:
            session['wishlist'].remove(str(product_id))
            session.modified = True

    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'wishlist_count': get_wishlist_count()
        })

    return redirect(url_for('wishlist'))

@app.route('/search')
def search():
    query = request.args.get('query', '')

    # Start with the base query for name and description
    search_query = Product.query.filter(Product.name.contains(query) | Product.description.contains(query))

    # Add category filtering for search results
    selected_categories = request.args.getlist('category')
    if selected_categories:
        search_query = search_query.filter(Product.category.in_(selected_categories))

    products = search_query.all()

    # For the category filter in the sidebar, get all unique categories from the search results
    available_categories = sorted(list(set([p.category for p in products if p.category])))

    return render_template('search_results.html', products=products, query=query, available_categories=available_categories)

@app.route('/plan')
def plan():
    return render_template('plan.html')

@app.route('/plan/six-pack-diet')
def six_pack_diet():
    return render_template('six_pack_diet.html')

@app.route('/plan/weight-gain-diet')
def weight_gain_diet():
    return render_template('weight_gain_diet.html')

@app.route('/plan/weight-loss-diet')
def weight_loss_diet():
    return render_template('weight_loss_diet.html')

@app.route('/purchase_plan/<plan_name>')
def purchase_plan(plan_name):
    # In a real application, this would involve payment processing
    # For this simulation, we will just show a confirmation page
    # You would also likely associate the purchased plan with the user
    return render_template('plan_purchase_confirmation.html', plan_name=plan_name)

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_items = []
    total = 0

    # User is logged in, get cart from database
    cart_items = CartItem.query.filter_by(user_id=session['user_id']).all()
    total = sum(item.product.discounted_price * item.quantity for item in cart_items)

    # If cart is empty, redirect to cart page
    if not cart_items:
        return redirect(url_for('cart'))

    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    new_quantity = int(request.form.get('quantity', 1))

    if 'user_id' in session:
        # User is logged in, update database cart
        user_id = session['user_id']
        cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item:
            if new_quantity > 0:
                cart_item.quantity = new_quantity
            else:
                # If quantity is 0 or less, remove the item
                db.session.delete(cart_item)
            db.session.commit()
    else:
        # User is not logged in, update session cart
        if 'cart' in session and str(product_id) in session['cart']:
            if new_quantity > 0:
                session['cart'][str(product_id)] = new_quantity
            else:
                # Remove item if quantity is 0 or less
                session['cart'].pop(str(product_id), None)
            session.modified = True

    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'cart_count': get_cart_count()
        })

    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'user_id' in session:
        # User is logged in, remove from database cart
        user_id = session['user_id']
        cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    else:
        # User is not logged in, remove from session cart
        if 'cart' in session and str(product_id) in session['cart']:
            session['cart'].pop(str(product_id), None)
            session.modified = True

    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'cart_count': get_cart_count()
        })

    return redirect(url_for('cart'))

@app.route('/offers')
def offers():
    return render_template('offers.html')

@app.route('/gift_cards')
def gift_cards():
    return render_template('gift_cards.html')

# Manual initialization endpoint (for troubleshooting)
@app.route('/init_db')
def init_db():
    # Create all tables
    db.create_all()

    # Initialize with sample data
    success = create_sample_data()

    if success:
        return "Database initialized with sample data. <a href='/'>Go to home page</a>"
    else:
        return "Error initializing database. Check server logs for details. <a href='/'>Go to home page</a>"

if __name__ == '__main__':
    # Make sure database is created
    with app.app_context():
        db.create_all()

    app.run(debug=True)