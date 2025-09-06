# RentAssured Advanced Database Structure

## Overview

The RentAssured Advanced Database is a comprehensive marketplace database designed to support all the features of a modern peer-to-peer rental and freelancing platform. It includes advanced features like user roles, payment processing, messaging, notifications, and much more.

## Database Features

### 🏗️ **Core Architecture**
- **16 Tables** with proper relationships and constraints
- **User Roles & Permissions** system
- **Advanced Booking System** with cancellation policies
- **Payment Processing** with multiple payment methods
- **Messaging & Notifications** system
- **Review & Rating** system
- **Wishlist & Favorites** functionality
- **Coupon & Discount** system
- **Audit Logging** for security and compliance

### 📊 **Database Schema**

#### 1. **User Management**
- **`roles`** - User roles (renter, owner, freelancer, admin, moderator)
- **`users`** - Enhanced user profiles with verification and status tracking

#### 2. **Content Management**
- **`categories`** - Hierarchical category system with parent-child relationships
- **`listings`** - Products and services with advanced metadata
- **`listing_images`** - Separate image management with primary/secondary images

#### 3. **Booking & Transactions**
- **`bookings`** - Advanced booking system with status tracking
- **`cancellation_policies`** - Flexible cancellation policies
- **`payment_methods`** - User payment method management
- **`payments`** - Transaction tracking with gateway integration

#### 4. **Social Features**
- **`reviews`** - Enhanced review system with verification and flagging
- **`messages`** - User-to-user messaging system
- **`notifications`** - System notifications with read tracking
- **`wishlists`** - User wishlist functionality

#### 5. **Business Features**
- **`coupons`** - Discount coupon system
- **`coupon_usage`** - Coupon usage tracking
- **`audit_logs`** - Security and compliance logging

## 🚀 **Quick Start**

### 1. **Setup Advanced Database**
```bash
python setup_advanced_database.py
```

### 2. **Migrate Existing Data (Optional)**
```bash
python migrate_to_advanced.py
```

### 3. **Run Advanced Application**
```bash
python app_advanced.py
```

## 📋 **Table Details**

### **Users & Roles**

#### `roles` Table
```sql
CREATE TABLE roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Default Roles:**
- `renter` - Regular users who rent items/services
- `owner` - Users who list items for rent
- `freelancer` - Users who provide freelance services
- `admin` - System administrators
- `moderator` - Content moderators

#### `users` Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INT DEFAULT 1,
    profile_picture VARCHAR(255),
    bio TEXT,
    location VARCHAR(200),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_suspended BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### **Listings & Categories**

#### `categories` Table
```sql
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    parent_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `listings` Table
```sql
CREATE TABLE listings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    location VARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    owner_id INT NOT NULL,
    type ENUM('product', 'service') DEFAULT 'product',
    availability JSON,
    status ENUM('draft', 'active', 'inactive', 'suspended') DEFAULT 'draft',
    featured BOOLEAN DEFAULT FALSE,
    views_count INT DEFAULT 0,
    likes_count INT DEFAULT 0,
    rating_avg DECIMAL(3,2) DEFAULT 0.00,
    reviews_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `listing_images` Table
```sql
CREATE TABLE listing_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    listing_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(200),
    sort_order INT DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Booking System**

#### `bookings` Table
```sql
CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    listing_id INT NOT NULL,
    renter_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    security_deposit DECIMAL(10,2) DEFAULT 0.00,
    service_fee DECIMAL(10,2) DEFAULT 0.00,
    status ENUM('pending', 'confirmed', 'cancelled', 'completed', 'disputed') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'refunded', 'partial_refund') DEFAULT 'pending',
    cancellation_policy_id INT,
    cancellation_reason TEXT,
    cancellation_date TIMESTAMP NULL,
    special_requests TEXT,
    owner_notes TEXT,
    renter_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `cancellation_policies` Table
```sql
CREATE TABLE cancellation_policies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    penalty_percentage DECIMAL(5,2) DEFAULT 0.00,
    effective_duration_hours INT DEFAULT 24,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### **Payment System**

#### `payment_methods` Table
```sql
CREATE TABLE payment_methods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM('card', 'upi', 'netbanking', 'wallet') NOT NULL,
    provider VARCHAR(50) NOT NULL,
    account_details JSON,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `payments` Table
```sql
CREATE TABLE payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    payment_method_id INT,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    transaction_id VARCHAR(100) UNIQUE,
    gateway_transaction_id VARCHAR(100),
    gateway_response JSON,
    status ENUM('pending', 'success', 'failed', 'refunded', 'partial_refund') DEFAULT 'pending',
    payment_type ENUM('booking', 'deposit', 'refund', 'penalty') DEFAULT 'booking',
    failure_reason TEXT,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### **Social Features**

#### `reviews` Table
```sql
CREATE TABLE reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    listing_id INT NOT NULL,
    booking_id INT,
    reviewer_id INT NOT NULL,
    reviewee_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    response TEXT,
    response_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `messages` Table
```sql
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    booking_id INT,
    subject VARCHAR(200),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `notifications` Table
```sql
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM('booking', 'payment', 'message', 'review', 'system') NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSON,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Business Features**

#### `coupons` Table
```sql
CREATE TABLE coupons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type ENUM('percentage', 'fixed') NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    min_amount DECIMAL(10,2) DEFAULT 0.00,
    max_discount DECIMAL(10,2) NULL,
    usage_limit INT NULL,
    used_count INT DEFAULT 0,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### `audit_logs` Table
```sql
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 **Key Features**

### **1. User Roles & Permissions**
- Hierarchical role system
- JSON-based permissions
- User verification and suspension

### **2. Advanced Listings**
- Support for both products and services
- Multiple images with primary/secondary designation
- Availability scheduling
- Featured listings
- View and like tracking

### **3. Smart Booking System**
- Date validation and overlap checking
- Cancellation policies
- Service fee calculation
- Special requests handling

### **4. Payment Processing**
- Multiple payment methods
- Transaction tracking
- Gateway integration support
- Refund handling

### **5. Social Features**
- User-to-user messaging
- Review and rating system
- Notification system
- Wishlist functionality

### **6. Business Tools**
- Coupon and discount system
- Audit logging
- Analytics support
- Content moderation

## 📈 **Performance Optimizations**

- **Indexes** on frequently queried columns
- **Full-text search** on listings
- **JSON fields** for flexible data storage
- **Proper foreign key constraints**
- **Cascading deletes** for data integrity

## 🔒 **Security Features**

- **Audit logging** for all critical operations
- **User verification** system
- **Account suspension** capabilities
- **Review flagging** system
- **IP tracking** for security

## 🚀 **Migration Guide**

### **From Basic to Advanced Database**

1. **Backup your current database**
2. **Run the advanced database setup**
3. **Run the migration script**
4. **Update your application code**
5. **Test thoroughly**

### **Migration Script Usage**
```bash
# Setup advanced database
python setup_advanced_database.py

# Migrate existing data
python migrate_to_advanced.py

# Run advanced application
python app_advanced.py
```

## 📚 **API Endpoints**

The advanced application includes additional API endpoints:

- `GET /api/categories` - Get all active categories
- `GET /api/coupons/<code>` - Validate coupon code
- `POST /book_listing` - Create booking with advanced features
- `GET /dashboard` - Enhanced dashboard with role-based content

## 🎯 **Next Steps**

1. **Test the new database structure**
2. **Update your frontend to use new features**
3. **Implement payment gateway integration**
4. **Add real-time messaging**
5. **Set up notification system**
6. **Configure audit logging**

## 📞 **Support**

For questions or issues with the advanced database structure, please refer to the code comments and this documentation. The database is designed to be scalable and maintainable for a production marketplace application.
