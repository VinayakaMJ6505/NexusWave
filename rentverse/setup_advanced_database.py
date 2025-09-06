#!/usr/bin/env python3
"""
Advanced RentAssured Database Setup Script
Creates a comprehensive marketplace database with advanced features
"""

import pymysql
import sys
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Gagan@2114',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

DATABASE_NAME = 'rentassured_advanced'

def create_database():
    """Create the main database"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{DATABASE_NAME}' created successfully")
        
        # Use the database
        cursor.execute(f"USE {DATABASE_NAME}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        connection = pymysql.connect(**DB_CONFIG, database=DATABASE_NAME)
        cursor = connection.cursor()
        
        # 1. User Roles Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INT PRIMARY KEY AUTO_INCREMENT,
                role_name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                permissions JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)
        
        # 2. Users Table (Enhanced)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL,
                INDEX idx_email (email),
                INDEX idx_phone (phone),
                INDEX idx_role (role_id),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB
        """)
        
        # 3. Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                icon VARCHAR(100),
                parent_id INT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                sort_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
                INDEX idx_parent (parent_id),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB
        """)
        
        # 4. Listings Table (Enhanced)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS listings (
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_category (category_id),
                INDEX idx_owner (owner_id),
                INDEX idx_status (status),
                INDEX idx_type (type),
                INDEX idx_featured (featured),
                INDEX idx_price (price),
                INDEX idx_location (location),
                FULLTEXT idx_search (title, description, location)
            ) ENGINE=InnoDB
        """)
        
        # 5. Listing Images Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS listing_images (
                id INT PRIMARY KEY AUTO_INCREMENT,
                listing_id INT NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                alt_text VARCHAR(200),
                sort_order INT DEFAULT 0,
                is_primary BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
                INDEX idx_listing (listing_id),
                INDEX idx_primary (is_primary),
                INDEX idx_sort (sort_order)
            ) ENGINE=InnoDB
        """)
        
        # 6. Cancellation Policies Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cancellation_policies (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                penalty_percentage DECIMAL(5,2) DEFAULT 0.00,
                effective_duration_hours INT DEFAULT 24,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)
        
        # 7. Bookings Table (Enhanced)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
                FOREIGN KEY (renter_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (cancellation_policy_id) REFERENCES cancellation_policies(id) ON DELETE SET NULL,
                INDEX idx_listing (listing_id),
                INDEX idx_renter (renter_id),
                INDEX idx_status (status),
                INDEX idx_payment_status (payment_status),
                INDEX idx_dates (start_date, end_date)
            ) ENGINE=InnoDB
        """)
        
        # 8. Payment Methods Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                type ENUM('card', 'upi', 'netbanking', 'wallet') NOT NULL,
                provider VARCHAR(50) NOT NULL,
                account_details JSON,
                is_default BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user (user_id),
                INDEX idx_type (type),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB
        """)
        
        # 9. Payments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
                FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id) ON DELETE SET NULL,
                INDEX idx_booking (booking_id),
                INDEX idx_transaction (transaction_id),
                INDEX idx_status (status),
                INDEX idx_type (payment_type)
            ) ENGINE=InnoDB
        """)
        
        # 10. Reviews Table (Enhanced)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
                FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (reviewee_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_booking_review (booking_id),
                INDEX idx_listing (listing_id),
                INDEX idx_reviewer (reviewer_id),
                INDEX idx_reviewee (reviewee_id),
                INDEX idx_rating (rating),
                INDEX idx_verified (is_verified)
            ) ENGINE=InnoDB
        """)
        
        # 11. Messages Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT PRIMARY KEY AUTO_INCREMENT,
                sender_id INT NOT NULL,
                receiver_id INT NOT NULL,
                booking_id INT,
                subject VARCHAR(200),
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                read_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE SET NULL,
                INDEX idx_sender (sender_id),
                INDEX idx_receiver (receiver_id),
                INDEX idx_booking (booking_id),
                INDEX idx_read (is_read),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB
        """)
        
        # 12. Notifications Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                type ENUM('booking', 'payment', 'message', 'review', 'system') NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                data JSON,
                is_read BOOLEAN DEFAULT FALSE,
                read_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user (user_id),
                INDEX idx_type (type),
                INDEX idx_read (is_read),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB
        """)
        
        # 13. Wishlists Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishlists (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                listing_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_listing (user_id, listing_id),
                INDEX idx_user (user_id),
                INDEX idx_listing (listing_id)
            ) ENGINE=InnoDB
        """)
        
        # 14. Coupons Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_code (code),
                INDEX idx_active (is_active),
                INDEX idx_validity (valid_from, valid_until)
            ) ENGINE=InnoDB
        """)
        
        # 15. Coupon Usage Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupon_usage (
                id INT PRIMARY KEY AUTO_INCREMENT,
                coupon_id INT NOT NULL,
                user_id INT NOT NULL,
                booking_id INT NOT NULL,
                discount_amount DECIMAL(10,2) NOT NULL,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
                UNIQUE KEY unique_booking_coupon (booking_id, coupon_id),
                INDEX idx_coupon (coupon_id),
                INDEX idx_user (user_id),
                INDEX idx_booking (booking_id)
            ) ENGINE=InnoDB
        """)
        
        # 16. Audit Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                action VARCHAR(100) NOT NULL,
                table_name VARCHAR(50),
                record_id INT,
                old_values JSON,
                new_values JSON,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_user (user_id),
                INDEX idx_action (action),
                INDEX idx_table (table_name),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB
        """)
        
        print("✅ All tables created successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def insert_initial_data():
    """Insert initial data into the database"""
    try:
        connection = pymysql.connect(**DB_CONFIG, database=DATABASE_NAME)
        cursor = connection.cursor()
        
        # Insert roles
        roles_data = [
            (1, 'renter', 'Regular user who rents items/services', '{"rent": true, "review": true}'),
            (2, 'owner', 'User who lists items/services for rent', '{"list": true, "manage": true, "review": true}'),
            (3, 'freelancer', 'User who provides freelance services', '{"list": true, "service": true, "manage": true, "review": true}'),
            (4, 'admin', 'System administrator', '{"admin": true, "manage": true, "moderate": true}'),
            (5, 'moderator', 'Content moderator', '{"moderate": true, "review": true}')
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO roles (id, role_name, description, permissions) 
            VALUES (%s, %s, %s, %s)
        """, roles_data)
        
        # Insert categories
        categories_data = [
            (1, 'Vehicles', 'Cars, bikes, and other vehicles', 'car', None, 1),
            (2, 'Electronics', 'Laptops, cameras, gadgets', 'laptop', None, 2),
            (3, 'Furniture', 'Home and office furniture', 'chair', None, 3),
            (4, 'Photography', 'Photography services and equipment', 'camera', None, 4),
            (5, 'Home Services', 'Cleaning, maintenance, repairs', 'tools', None, 5),
            (6, 'Professional Services', 'Consulting, tutoring, design', 'briefcase', None, 6),
            (7, 'Events', 'Event planning and equipment', 'calendar', None, 7),
            (8, 'Sports & Fitness', 'Sports equipment and fitness services', 'dumbbell', None, 8)
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO categories (id, name, description, icon, parent_id, sort_order) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, categories_data)
        
        # Insert cancellation policies
        policies_data = [
            (1, 'Flexible', 'Free cancellation up to 24 hours before start date', 0.00, 24),
            (2, 'Moderate', '50% refund if cancelled 48 hours before start date', 50.00, 48),
            (3, 'Strict', 'No refund for cancellations less than 7 days before start date', 100.00, 168)
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO cancellation_policies (id, name, description, penalty_percentage, effective_duration_hours) 
            VALUES (%s, %s, %s, %s, %s)
        """, policies_data)
        
        # Insert sample coupons
        coupons_data = [
            (1, 'WELCOME10', 'Welcome Discount', 'Get 10% off on your first booking', 'percentage', 10.00, 500.00, 1000.00, 100, 0, datetime.now(), datetime.now() + timedelta(days=30)),
            (2, 'SAVE500', 'Fixed Discount', 'Save ₹500 on bookings above ₹2000', 'fixed', 500.00, 2000.00, 500.00, 50, 0, datetime.now(), datetime.now() + timedelta(days=60))
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO coupons (id, code, name, description, type, value, min_amount, max_discount, usage_limit, used_count, valid_from, valid_until) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, coupons_data)
        
        connection.commit()
        print("✅ Initial data inserted successfully")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error inserting initial data: {e}")
        return False

def main():
    """Main function to set up the database"""
    print("🚀 Setting up RentAssured Advanced Database...")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    if not create_tables():
        sys.exit(1)
    
    # Step 3: Insert initial data
    if not insert_initial_data():
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Database setup completed successfully!")
    print(f"📊 Database: {DATABASE_NAME}")
    print("📋 Tables created: 16")
    print("🔧 Features included:")
    print("   • User roles and permissions")
    print("   • Enhanced listings with images")
    print("   • Advanced booking system")
    print("   • Payment transactions")
    print("   • Reviews and ratings")
    print("   • Messaging system")
    print("   • Notifications")
    print("   • Wishlists")
    print("   • Coupons and discounts")
    print("   • Audit logging")
    print("   • Cancellation policies")

if __name__ == "__main__":
    main()
