"""
Advanced RentAssured Models
Enhanced database models with advanced marketplace features
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

# User Roles Model
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='role', lazy=True)

# Enhanced User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=1)
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    location = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_suspended = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    reset_token = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    listings = db.relationship('Listing', backref='owner', lazy=True)
    bookings_as_renter = db.relationship('Booking', foreign_keys='Booking.renter_id', backref='renter', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee', lazy=True)
    payment_methods = db.relationship('PaymentMethod', backref='user', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    wishlists = db.relationship('Wishlist', backref='user', lazy=True)
    coupon_usage = db.relationship('CouponUsage', backref='user', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

# Enhanced Category Model
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    listings = db.relationship('Listing', backref='category', lazy=True)
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))

# Enhanced Listing Model
class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum('product', 'service', name='listing_type'), default='product')
    availability = db.Column(db.JSON)
    status = db.Column(db.Enum('draft', 'active', 'inactive', 'suspended', name='listing_status'), default='draft')
    featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    rating_avg = db.Column(db.Numeric(3, 2), default=0.00)
    reviews_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = db.relationship('ListingImage', backref='listing', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='listing', lazy=True)
    reviews = db.relationship('Review', backref='listing', lazy=True)
    wishlists = db.relationship('Wishlist', backref='listing', lazy=True)

# Listing Images Model
class ListingImage(db.Model):
    __tablename__ = 'listing_images'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    sort_order = db.Column(db.Integer, default=0)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Cancellation Policy Model
class CancellationPolicy(db.Model):
    __tablename__ = 'cancellation_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    penalty_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    effective_duration_hours = db.Column(db.Integer, default=24)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='cancellation_policy', lazy=True)

# Enhanced Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    security_deposit = db.Column(db.Numeric(10, 2), default=0.00)
    service_fee = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'completed', 'disputed', name='booking_status'), default='pending')
    payment_status = db.Column(db.Enum('pending', 'paid', 'refunded', 'partial_refund', name='payment_status'), default='pending')
    cancellation_policy_id = db.Column(db.Integer, db.ForeignKey('cancellation_policies.id'))
    cancellation_reason = db.Column(db.Text)
    cancellation_date = db.Column(db.DateTime)
    special_requests = db.Column(db.Text)
    owner_notes = db.Column(db.Text)
    renter_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy=True)
    reviews = db.relationship('Review', backref='booking', lazy=True)
    messages = db.relationship('Message', backref='booking', lazy=True)
    coupon_usage = db.relationship('CouponUsage', backref='booking', lazy=True)

# Payment Method Model
class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum('card', 'upi', 'netbanking', 'wallet', name='payment_type'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    account_details = db.Column(db.JSON)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='payment_method', lazy=True)

# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='INR')
    transaction_id = db.Column(db.String(100), unique=True)
    gateway_transaction_id = db.Column(db.String(100))
    gateway_response = db.Column(db.JSON)
    status = db.Column(db.Enum('pending', 'success', 'failed', 'refunded', 'partial_refund', name='payment_status'), default='pending')
    payment_type = db.Column(db.Enum('booking', 'deposit', 'refund', 'penalty', name='payment_type'), default='booking')
    failure_reason = db.Column(db.Text)
    processed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Enhanced Review Model
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.Text)
    response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        if 'rating' in kwargs:
            kwargs['rating'] = max(1, min(5, kwargs['rating']))
        super(Review, self).__init__(**kwargs)

# Message Model
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum('booking', 'payment', 'message', 'review', 'system', name='notification_type'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Wishlist Model
class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'listing_id', name='unique_user_listing'),)

# Coupon Model
class Coupon(db.Model):
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.Enum('percentage', 'fixed', name='coupon_type'), nullable=False)
    value = db.Column(db.Numeric(10, 2), nullable=False)
    min_amount = db.Column(db.Numeric(10, 2), default=0.00)
    max_discount = db.Column(db.Numeric(10, 2))
    usage_limit = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usage = db.relationship('CouponUsage', backref='coupon', lazy=True)

# Coupon Usage Model
class CouponUsage(db.Model):
    __tablename__ = 'coupon_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('booking_id', 'coupon_id', name='unique_booking_coupon'),)

# Audit Log Model
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions
def get_primary_image(listing):
    """Get the primary image for a listing"""
    primary_image = ListingImage.query.filter_by(
        listing_id=listing.id, 
        is_primary=True
    ).first()
    
    if primary_image:
        return primary_image.image_url
    
    # Fallback to first image
    first_image = ListingImage.query.filter_by(
        listing_id=listing.id
    ).order_by(ListingImage.sort_order).first()
    
    if first_image:
        return first_image.image_url
    
    return '/static/images/placeholder.jpg'

def calculate_booking_total(listing, start_date, end_date, coupon_code=None):
    """Calculate total booking amount including fees and discounts"""
    days = (end_date - start_date).days + 1
    base_amount = float(listing.price) * days
    service_fee = base_amount * 0.1  # 10% service fee
    total = base_amount + service_fee
    
    # Apply coupon discount if provided
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
        if coupon and coupon.valid_from <= datetime.now() <= coupon.valid_until:
            if coupon.type == 'percentage':
                discount = min(total * (coupon.value / 100), coupon.max_discount or total)
            else:  # fixed
                discount = coupon.value
            
            total = max(total - discount, 0)
    
    return {
        'base_amount': base_amount,
        'service_fee': service_fee,
        'discount': total - (base_amount + service_fee),
        'total': total
    }
