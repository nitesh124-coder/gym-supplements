# GYM SUPPLEMENTS AND NUTRITION PRODUCT Website

This is a GYM SUPPLEMENTS AND NUTRITION PRODUCT e-commerce website built using Python Flask, SQLite, and Bootstrap.

## Features

- Responsive design for all devices
- Product catalog with categories
- Product search functionality
- User registration and login
- Shopping cart functionality
- Product details with related products
- Sample product data included

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
https://github.com/nitesh124-coder/job-resume-analyzer
cd gym-supplements-nutrition-product

# Run the automated setup script
python setup.py
```

### Option 2: Manual Setup
```bash
# Clone the repository
https://github.com/nitesh124-coder/job-resume-analyzer
cd gym-supplements-nutrition-product

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Option 3: Test the Application
```bash
# Run the test suite to verify everything works
python test_app.py
```

## Starting the Application

1. Run the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to: `http://127.0.0.1:5000`

3. The application will automatically:
   - Create the SQLite database
   - Initialize with sample products
   - Create a test user account

## Default Login Credentials

- **Username:** test
- **Password:** password123

## Project Structure

```
gym-supplements-nutrition-product/
├── app.py                 # Main Flask application
├── setup.py              # Automated setup script
├── test_app.py           # Test suite
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   ├── cart.html       # Shopping cart
│   ├── login.html      # Login page
│   └── ...             # Other templates
├── static/             # Static files
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── images/        # Product images
└── instance/          # Database files (auto-created)
```

## Adding Images

The product images are currently using placeholders. To add real images:

1. Place image files in the `static/images/` directory
2. Update the database or edit the `app.py` file to point to the correct image paths

## Features

### Current Features
- ✅ Responsive design for all devices
- ✅ Product catalog with categories (Whey Protein, Mass Gainers, Pre-Workout, etc.)
- ✅ **Advanced product search and filtering** - Price range, brand, and discount filters
- ✅ User registration and authentication
- ✅ Shopping cart functionality (works for both logged-in and guest users)
- ✅ **Real-time cart count display** - Cart icon shows live count of items
- ✅ **AJAX cart operations** - Add to cart without page refresh
- ✅ **Animated cart updates** - Visual feedback when items are added
- ✅ **Complete wishlist functionality** - Save favorite products
- ✅ **Real-time wishlist count display** - Heart icon shows live count of items
- ✅ **AJAX wishlist operations** - Add to wishlist without page refresh
- ✅ **Animated wishlist updates** - Visual feedback when items are added
- ✅ **Wishlist page** - View and manage saved products
- ✅ Product details with related products
- ✅ Diet plans (Six Pack, Weight Gain, Weight Loss)
- ✅ Offers and gift cards pages
- ✅ Automatic database initialization with sample data
- ✅ Error handling and fallback mechanisms
- ✅ Session-based cart and wishlist for unauthenticated users

### Future Enhancements
- 🔄 Payment gateway integration
- 🔄 Order history and tracking
- 🔄 Admin dashboard for product management
- 🔄 Product reviews and ratings
- 🔄 Email notifications
- 🔄 Advanced user profile management
- 🔄 Inventory management
- 🔄 Coupon and discount system
- 🔄 Move wishlist items to cart functionality
- 🔄 Wishlist sharing and social features

## Troubleshooting

### Common Issues

1. **Database errors**: Run `python setup.py` to reinitialize
2. **Missing images**: The app uses placeholder images by default
3. **Port already in use**: Change the port in `app.py` or kill the existing process
4. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Getting Help

If you encounter any issues:
1. Run the test suite: `python test_app.py`
2. Check the console output for error messages
3. Ensure all required files are present
4. Verify Python version compatibility (3.8+)

## License

This project is for educational purposes only. This is not affiliated with any actual gym supplements or nutrition product website or brand.gym-supplements
