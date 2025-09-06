from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import json

# Import advanced models
from models_advanced import (
    db, Role, User, Category, Listing, ListingImage, CancellationPolicy,
    Booking, PaymentMethod, Payment, Review, Message, Notification,
    Wishlist, Coupon, CouponUsage, AuditLog,
    get_primary_image, calculate_booking_total
)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Gagan%402114@localhost/rentassured_advanced'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Custom Jinja2 filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert JSON string to Python object"""
    if value:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return []

@app.template_filter('get_first_image')
def get_first_image_filter(listing):
    """Get the first image from listing or return placeholder"""
    if hasattr(listing, 'images') and listing.images:
        # If it's a relationship, get the first image
        if hasattr(listing.images, '__iter__'):
            for img in listing.images:
                if img.is_primary:
                    return img.image_url
            # If no primary image, get the first one
            if listing.images:
                return listing.images[0].image_url
        # If it's a JSON string (old format)
        elif isinstance(listing.images, str):
            try:
                import json
                images = json.loads(listing.images)
                if images and len(images) > 0:
                    return images[0]
            except:
                pass
    return '/static/images/placeholder.jpg'

# Routes
@app.route('/')
def index():
    featured_listings = Listing.query.filter_by(status='active').order_by(Listing.featured.desc(), Listing.created_at.desc()).limit(8).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template('index.html', listings=featured_listings, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        # Validation
        if not data.get('name') or len(data['name'].strip()) < 2:
            return jsonify({'error': 'Name must be at least 2 characters long'}), 400
        
        if not data.get('email') or '@' not in data['email']:
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        if not data.get('phone') or len(data['phone'].strip()) < 10:
            return jsonify({'error': 'Please enter a valid phone number'}), 400
        
        if not data.get('password') or len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Validate user type/role
        role_id = 1  # Default to renter
        if data.get('user_type') == 'owner':
            role_id = 2
        elif data.get('user_type') == 'freelancer':
            role_id = 3
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(
            name=data['name'].strip(),
            email=data['email'].strip().lower(),
            phone=data['phone'].strip(),
            password=hashed_password,
            role_id=role_id,
            location=data.get('location', '').strip()
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and bcrypt.check_password_hash(user.password, data['password']):
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 401
            
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role.role_name if user.role else 'renter'
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Get token from URL parameter
    token = request.args.get('token')
    user_id = None
    
    if token:
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = int(decoded_token['sub'])
        except Exception as e:
            print(f"Token validation error: {e}")
            user_id = 1  # Fallback for testing
    
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's listings (all users can have listings)
    listings = Listing.query.filter_by(owner_id=user_id).all()
    active_listings = Listing.query.filter_by(owner_id=user_id, status='active').all()
    
    # Get bookings based on user role
    if user.role.role_name in ['owner', 'freelancer']:
        bookings = Booking.query.join(Listing).filter(Listing.owner_id == user_id).all()
    else:
        bookings = Booking.query.filter_by(renter_id=user_id).all()
    
    # Debug: print(f"Dashboard - User {user_id} has {len(listings)} total listings, {len(active_listings)} active listings")
    
    return render_template('dashboard.html', user=user, listings=listings, active_listings=active_listings, bookings=bookings)

@app.route('/listings')
def listings():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 100000, type=float)
    listing_type = request.args.get('type', '')
    
    query = Listing.query.filter_by(status='active')
    
    if category:
        query = query.filter_by(category_id=category)
    if location:
        query = query.filter(Listing.location.contains(location))
    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    if listing_type:
        query = query.filter_by(type=listing_type)
    
    listings = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('listings.html', listings=listings, categories=categories)

@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    owner = User.query.get(listing.owner_id)
    reviews = Review.query.filter_by(listing_id=listing_id).all()
    cancellation_policies = CancellationPolicy.query.filter_by(is_active=True).all()
    
    return render_template('listing_detail.html', 
                         listing=listing, 
                         owner=owner, 
                         reviews=reviews,
                         cancellation_policies=cancellation_policies)

@app.route('/create_listing', methods=['GET', 'POST'])
def create_listing():
    # Get token from URL parameter or Authorization header
    token = request.args.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    user_id = None
    
    if token:
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = int(decoded_token['sub'])
            print(f"Create listing - Token validated successfully for user_id: {user_id}")
        except Exception as e:
            print(f"Create listing - Token validation error: {e}")
            print(f"Create listing - Token: {token[:50]}...")
            user_id = 1  # Fallback for testing
    
    # Get categories for the form
    categories = Category.query.all()
    
    # For GET requests, redirect to login if no token
    if request.method == 'GET' and not user_id:
        # Check if user is logged in via localStorage (frontend will handle this)
        return render_template('create_listing.html', categories=categories)
    
    # For POST requests, return JSON error if no token
    if request.method == 'POST' and not user_id:
        print(f"Create listing - No user_id found, token: {token}")
        return jsonify({'error': 'Authentication required'}), 401
    
    if request.method == 'POST':
        data = request.get_json()
        print(f"Create listing - Received data: {data}")
        
        # Comprehensive validation
        if not data.get('title') or len(data['title'].strip()) < 3:
            return jsonify({'error': 'Title must be at least 3 characters long'}), 400
        if len(data['title'].strip()) > 100:
            return jsonify({'error': 'Title cannot exceed 100 characters'}), 400
        
        if not data.get('description') or len(data['description'].strip()) < 10:
            return jsonify({'error': 'Description must be at least 10 characters long'}), 400
        if len(data['description'].strip()) > 1000:
            return jsonify({'error': 'Description cannot exceed 1000 characters'}), 400
        
        try:
            price = float(data['price'])
            if price <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 400
            if price < 1:
                return jsonify({'error': 'Price must be at least ₹1'}), 400
            if price > 1000000:
                return jsonify({'error': 'Price cannot exceed ₹10,00,000'}), 400
            # Check for more than 2 decimal places
            if round(price, 2) != price:
                return jsonify({'error': 'Price can only have up to 2 decimal places'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid price format'}), 400
        
        if not data.get('location') or len(data['location'].strip()) < 3:
            return jsonify({'error': 'Location must be at least 3 characters long'}), 400
        if len(data['location'].strip()) > 100:
            return jsonify({'error': 'Location cannot exceed 100 characters'}), 400
        
        # Validate category exists
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Invalid category selected'}), 400
        
        # Validate listing type
        listing_type = data.get('type', 'product')
        if listing_type not in ['product', 'service']:
            return jsonify({'error': 'Invalid listing type'}), 400
        
        listing = Listing(
            title=data['title'].strip(),
            description=data['description'].strip(),
            price=price,
            location=data['location'].strip(),
            category_id=data['category_id'],
            owner_id=user_id,
            type=listing_type,
            availability=json.dumps(data.get('availability', {})),
            status='active'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Handle images if provided
        if data.get('images'):
            for i, image_url in enumerate(data['images']):
                image = ListingImage(
                    listing_id=listing.id,
                    image_url=image_url,
                    sort_order=i,
                    is_primary=(i == 0)
                )
                db.session.add(image)
        
        db.session.commit()
        
        return jsonify({'message': 'Listing created successfully'}), 201
    
    # For GET requests with valid token, render the form
    return render_template('create_listing.html', categories=categories)

@app.route('/book_listing', methods=['POST'])
def book_listing():
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    user_id = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = int(decoded_token['sub'])
        except Exception as e:
            print(f"Token validation error: {e}")
            user_id = 1  # Fallback for testing
    
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    
    try:
        # Validation
        if not data.get('start_date') or not data.get('end_date'):
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Check if dates are valid
        if start_date < datetime.now().date():
            return jsonify({'error': 'Start date cannot be in the past'}), 400
        
        if end_date <= start_date:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        # Check if booking is not too far in the future (max 1 year)
        max_future_date = datetime.now().date() + timedelta(days=365)
        if start_date > max_future_date:
            return jsonify({'error': 'Booking cannot be more than 1 year in advance'}), 400
        
        # Validate listing exists and is available
        listing = Listing.query.get(data['listing_id'])
        if not listing:
            return jsonify({'error': 'Listing not found'}), 404
        
        if listing.status != 'active':
            return jsonify({'error': 'This listing is not available for booking'}), 400
        
        # Calculate total amount
        booking_calculation = calculate_booking_total(
            listing, start_date, end_date, data.get('coupon_code')
        )
        
        # Check for overlapping bookings
        existing_booking = Booking.query.filter(
            Booking.listing_id == data['listing_id'],
            Booking.status.in_(['pending', 'confirmed']),
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        ).first()
        
        if existing_booking:
            return jsonify({'error': 'This listing is already booked for the selected dates'}), 400
        
        booking = Booking(
            listing_id=data['listing_id'],
            renter_id=user_id,
            start_date=start_date,
            end_date=end_date,
            total_amount=booking_calculation['total'],
            service_fee=booking_calculation['service_fee'],
            cancellation_policy_id=data.get('cancellation_policy_id'),
            special_requests=data.get('special_requests', '')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Apply coupon if used
        if data.get('coupon_code'):
            coupon = Coupon.query.filter_by(code=data['coupon_code'], is_active=True).first()
            if coupon:
                coupon_usage = CouponUsage(
                    coupon_id=coupon.id,
                    user_id=user_id,
                    booking_id=booking.id,
                    discount_amount=booking_calculation['discount']
                )
                db.session.add(coupon_usage)
                coupon.used_count += 1
                db.session.commit()
        
        print(f"Booking created successfully for user {user_id}")
        
        return jsonify({'message': 'Booking request sent successfully'}), 201
        
    except ValueError as e:
        print(f"Date parsing error: {e}")
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400
    except Exception as e:
        print(f"Booking creation error: {e}")
        return jsonify({'error': 'Failed to create booking'}), 500

@app.route('/api/categories')
def get_categories():
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'description': cat.description,
        'icon': cat.icon
    } for cat in categories])

@app.route('/test_cancellation')
def test_cancellation():
    """Test route for cancellation features"""
    return jsonify({'message': 'Cancellation features are working!'})

@app.route('/login_test')
def login_test():
    """Test page for login debugging"""
    return render_template('login_test.html')

@app.route('/api/user_bookings')
def get_user_bookings():
    """Get user's bookings"""
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authentication required'}), 401
    
    token = auth_header.split(' ')[1]
    user_id = None
    
    try:
        from flask_jwt_extended import decode_token
        decoded_token = decode_token(token)
        user_id = int(decoded_token['sub'])
    except Exception as e:
        print(f"Token validation error: {e}")
        return jsonify({'error': 'Invalid token'}), 401
    
    # Get user's bookings
    bookings = Booking.query.filter_by(renter_id=user_id).order_by(Booking.created_at.desc()).all()
    
    return jsonify([{
        'id': booking.id,
        'listing_id': booking.listing_id,
        'start_date': booking.start_date.isoformat(),
        'end_date': booking.end_date.isoformat(),
        'total_amount': float(booking.total_amount),
        'status': booking.status,
        'payment_status': booking.payment_status,
        'created_at': booking.created_at.isoformat(),
        'listing_title': booking.listing.title
    } for booking in bookings])

@app.route('/api/cancellation_policies')
def get_cancellation_policies():
    """Get all cancellation policies"""
    policies = CancellationPolicy.query.all()
    return jsonify([{
        'id': policy.id,
        'name': policy.name,
        'description': policy.description,
        'effective_duration_hours': policy.effective_duration_hours,
        'penalty_percentage': float(policy.penalty_percentage),
        'is_active': policy.is_active
    } for policy in policies])

@app.route('/api/coupons/<coupon_code>')
def validate_coupon(coupon_code):
    coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
    
    if not coupon:
        return jsonify({'error': 'Invalid coupon code'}), 404
    
    if coupon.valid_from > datetime.now() or coupon.valid_until < datetime.now():
        return jsonify({'error': 'Coupon has expired'}), 400
    
    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        return jsonify({'error': 'Coupon usage limit exceeded'}), 400
    
    return jsonify({
        'id': coupon.id,
        'code': coupon.code,
        'name': coupon.name,
        'type': coupon.type,
        'value': float(coupon.value),
        'min_amount': float(coupon.min_amount),
        'max_discount': float(coupon.max_discount) if coupon.max_discount else None
    })

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking with refund calculation"""
    # Get token from URL parameter or Authorization header
    token = request.args.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    user_id = None
    
    if token:
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = int(decoded_token['sub'])
        except Exception as e:
            print(f"Token validation error: {e}")
            user_id = 1  # Fallback for testing
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json() or {}
    cancellation_reason = data.get('reason', 'No reason provided')
    
    # Get the booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if user has permission to cancel (owner or renter)
    if booking.renter_id != user_id and booking.listing.owner_id != user_id:
        return jsonify({'error': 'You do not have permission to cancel this booking'}), 403
    
    # Check if booking can be cancelled
    if booking.status in ['cancelled', 'completed']:
        return jsonify({'error': 'Booking cannot be cancelled'}), 400
    
    # Calculate refund based on cancellation policy
    refund_amount = 0
    penalty_amount = 0
    
    if booking.cancellation_policy:
        policy = booking.cancellation_policy
        days_until_start = (booking.start_date - datetime.now().date()).days
        
        if days_until_start >= (policy.effective_duration_hours / 24):
            # Full refund
            refund_amount = float(booking.total_amount)
        else:
            # Partial refund based on penalty
            penalty_percentage = float(policy.penalty_percentage)
            penalty_amount = float(booking.total_amount) * (penalty_percentage / 100)
            refund_amount = float(booking.total_amount) - penalty_amount
    
    # Update booking status
    booking.status = 'cancelled'
    booking.cancellation_reason = cancellation_reason
    booking.cancellation_date = datetime.now()
    booking.payment_status = 'refunded' if refund_amount > 0 else 'pending'
    
    db.session.commit()
    
    # Create refund payment record if applicable
    if refund_amount > 0:
        refund_payment = Payment(
            booking_id=booking.id,
            amount=refund_amount,
            payment_type='refund',
            status='success',
            processed_at=datetime.now()
        )
        db.session.add(refund_payment)
        db.session.commit()
    
    return jsonify({
        'message': 'Booking cancelled successfully',
        'refund_amount': refund_amount,
        'penalty_amount': penalty_amount,
        'cancellation_date': booking.cancellation_date.isoformat()
    }), 200

@app.route('/deactivate_listing/<int:listing_id>', methods=['POST'])
def deactivate_listing(listing_id):
    """Deactivate a listing"""
    # Get token from URL parameter or Authorization header
    token = request.args.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    user_id = None
    
    if token:
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = int(decoded_token['sub'])
        except Exception as e:
            print(f"Token validation error: {e}")
            user_id = 1  # Fallback for testing
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get the listing
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    # Check if user owns the listing
    if listing.owner_id != user_id:
        return jsonify({'error': 'You do not have permission to deactivate this listing'}), 403
    
    # Check if there are any active bookings
    active_bookings = Booking.query.filter(
        Booking.listing_id == listing_id,
        Booking.status.in_(['pending', 'confirmed']),
        Booking.start_date > datetime.now().date()
    ).count()
    
    if active_bookings > 0:
        return jsonify({
            'error': f'Cannot deactivate listing with {active_bookings} active bookings. Please cancel them first.'
        }), 400
    
    # Deactivate the listing
    listing.status = 'inactive'
    db.session.commit()
    
    return jsonify({'message': 'Listing deactivated successfully'}), 200

@app.route('/reactivate_listing/<int:listing_id>', methods=['POST'])
def reactivate_listing(listing_id):
    """Reactivate a listing"""
    # Get token from URL parameter or Authorization header
    token = request.args.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    user_id = None
    
    if token:
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = int(decoded_token['sub'])
        except Exception as e:
            print(f"Token validation error: {e}")
            user_id = 1  # Fallback for testing
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get the listing
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    # Check if user owns the listing
    if listing.owner_id != user_id:
        return jsonify({'error': 'You do not have permission to reactivate this listing'}), 403
    
    # Reactivate the listing
    listing.status = 'active'
    db.session.commit()
    
    return jsonify({'message': 'Listing reactivated successfully'}), 200

@app.route('/delete_listing/<int:listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    """Delete a listing (only if no bookings exist)"""
    # Get token from URL parameter or Authorization header
    token = request.args.get('token')
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    user_id = None
    
    if token:
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = int(decoded_token['sub'])
        except Exception as e:
            print(f"Token validation error: {e}")
            user_id = 1  # Fallback for testing
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get the listing
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    # Check if user owns the listing
    if listing.owner_id != user_id:
        return jsonify({'error': 'You do not have permission to delete this listing'}), 403
    
    # Check if there are any bookings (even completed ones)
    bookings_count = Booking.query.filter_by(listing_id=listing_id).count()
    
    if bookings_count > 0:
        return jsonify({
            'error': f'Cannot delete listing with {bookings_count} bookings. Please deactivate instead.'
        }), 400
    
    # Delete the listing and its images
    ListingImage.query.filter_by(listing_id=listing_id).delete()
    db.session.delete(listing)
    db.session.commit()
    
    return jsonify({'message': 'Listing deleted successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default roles if they don't exist
        if not Role.query.first():
            roles = [
                Role(role_name='renter', description='Regular user who rents items/services'),
                Role(role_name='owner', description='User who lists items/services for rent'),
                Role(role_name='freelancer', description='User who provides freelance services'),
                Role(role_name='admin', description='System administrator'),
                Role(role_name='moderator', description='Content moderator')
            ]
            for role in roles:
                db.session.add(role)
            db.session.commit()
        
        # Create default categories if they don't exist
        if not Category.query.first():
            categories = [
                Category(name='Vehicles', description='Cars, bikes, and other vehicles', icon='car'),
                Category(name='Electronics', description='Laptops, cameras, gadgets', icon='laptop'),
                Category(name='Furniture', description='Home and office furniture', icon='chair'),
                Category(name='Photography', description='Photography services and equipment', icon='camera'),
                Category(name='Home Services', description='Cleaning, maintenance, repairs', icon='tools'),
                Category(name='Professional Services', description='Consulting, tutoring, design', icon='briefcase')
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
    
    app.run(debug=True)
