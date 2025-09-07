#!/usr/bin/env python3
"""
Database setup script for RentAssured
This script creates the database and initializes it with sample data
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_database():
    """Create the rentassured database"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password'  # Replace with your MySQL password
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS rentassured")
        print("✅ Database 'rentassured' created successfully")
        
        # Use the database
        cursor.execute("USE rentassured")
        
        # Create tables
        create_tables(cursor)
        
        # Insert sample data
        insert_sample_data(cursor)
        
        connection.commit()
        print("✅ Database setup completed successfully")
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ MySQL connection closed")

def create_tables(cursor):
    """Create all required tables"""
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            phone VARCHAR(15) NOT NULL,
            password VARCHAR(255) NOT NULL,
            user_type VARCHAR(20) NOT NULL DEFAULT 'renter',
            profile_picture VARCHAR(255),
            is_verified BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    print("✅ Users table created")
    
    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            icon VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Categories table created")
    
    # Listings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listing (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            price FLOAT NOT NULL,
            location VARCHAR(200) NOT NULL,
            category_id INT NOT NULL,
            owner_id INT NOT NULL,
            images TEXT,
            availability VARCHAR(50) DEFAULT 'flexible',
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES category(id),
            FOREIGN KEY (owner_id) REFERENCES user(id)
        )
    """)
    print("✅ Listings table created")
    
    # Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            id INT AUTO_INCREMENT PRIMARY KEY,
            listing_id INT NOT NULL,
            renter_id INT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_amount FLOAT NOT NULL,
            security_deposit FLOAT DEFAULT 0,
            status VARCHAR(20) DEFAULT 'pending',
            payment_status VARCHAR(20) DEFAULT 'pending',
            special_requests TEXT,
            cancellation_reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (listing_id) REFERENCES listing(id),
            FOREIGN KEY (renter_id) REFERENCES user(id)
        )
    """)
    print("✅ Bookings table created")
    
    # Reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review (
            id INT AUTO_INCREMENT PRIMARY KEY,
            listing_id INT NOT NULL,
            reviewer_id INT NOT NULL,
            reviewee_id INT NOT NULL,
            rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (listing_id) REFERENCES listing(id),
            FOREIGN KEY (reviewer_id) REFERENCES user(id),
            FOREIGN KEY (reviewee_id) REFERENCES user(id)
        )
    """)
    print("✅ Reviews table created")

def insert_sample_data(cursor):
    """Insert sample data into the database"""
    
    # Insert categories
    categories = [
        ('Vehicles', 'Cars, bikes, and other vehicles', 'car'),
        ('Electronics', 'Laptops, cameras, gadgets', 'laptop'),
        ('Furniture', 'Home and office furniture', 'couch'),
        ('Photography', 'Photography services', 'camera'),
        ('Home Services', 'Cleaning, maintenance, repairs', 'home'),
        ('Professional Services', 'Consulting, tutoring, design', 'briefcase')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO category (name, description, icon) 
        VALUES (%s, %s, %s)
    """, categories)
    print("✅ Sample categories inserted")
    
    # Insert sample users
    users = [
        ('John Doe', 'john@example.com', '9876543210', 'password123', 'renter'),
        ('Jane Smith', 'jane@example.com', '9876543211', 'password123', 'owner'),
        ('Mike Johnson', 'mike@example.com', '9876543212', 'password123', 'both'),
        ('Sarah Wilson', 'sarah@example.com', '9876543213', 'password123', 'owner')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO user (name, email, phone, password, user_type) 
        VALUES (%s, %s, %s, %s, %s)
    """, users)
    print("✅ Sample users inserted")
    
    # Insert sample listings
    listings = [
        ('Professional DSLR Camera', 'Canon EOS R5 with 24-70mm lens. Perfect for events and photography.', 1500, 'Mumbai, Maharashtra', 1, 2, '["camera1.jpg", "camera2.jpg"]', 'flexible'),
        ('MacBook Pro 16-inch', '2023 MacBook Pro M2 Max, 32GB RAM, 1TB SSD. Great for development work.', 2000, 'Bangalore, Karnataka', 2, 2, '["laptop1.jpg"]', 'weekdays'),
        ('Office Chair - Ergonomic', 'Herman Miller Aeron chair. Excellent condition, very comfortable.', 300, 'Delhi, NCR', 3, 3, '["chair1.jpg"]', 'flexible'),
        ('Wedding Photography Package', 'Professional wedding photography with 2 photographers, 8 hours coverage.', 25000, 'Pune, Maharashtra', 4, 4, '["wedding1.jpg"]', 'weekends'),
        ('Home Cleaning Service', 'Complete home cleaning including kitchen, bathrooms, and living areas.', 800, 'Chennai, Tamil Nadu', 5, 4, '["cleaning1.jpg"]', 'flexible'),
        ('Car - Honda City', '2022 Honda City, automatic transmission, well maintained.', 1200, 'Hyderabad, Telangana', 1, 3, '["car1.jpg"]', 'flexible')
    ]
    
    cursor.executemany("""
        INSERT IGNORE INTO listing (title, description, price, location, category_id, owner_id, images, availability) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, listings)
    print("✅ Sample listings inserted")

if __name__ == "__main__":
    print("🚀 Setting up RentAssured database...")
    print("=" * 50)
    
    # Check if MySQL is running
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Gagan@2114'  # Your MySQL password
        )
        connection.close()
    except Error as e:
        print(f"❌ Cannot connect to MySQL: {e}")
        print("Please make sure MySQL is running and update the password in this script")
        sys.exit(1)
    
    create_database()
    print("=" * 50)
    print("🎉 Database setup completed!")
    print("\nNext steps:")
    print("1. Update the database password in app.py if different")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")

