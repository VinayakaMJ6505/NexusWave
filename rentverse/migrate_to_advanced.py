#!/usr/bin/env python3
"""
Migration Script: RentAssured Basic to Advanced Database
Migrates data from the old database structure to the new advanced structure
"""

import pymysql
import sys
from datetime import datetime

# Database configurations
OLD_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Gagan@2114',
    'database': 'rentassured',
    'charset': 'utf8mb4'
}

NEW_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Gagan@2114',
    'database': 'rentassured_advanced',
    'charset': 'utf8mb4'
}

def migrate_users():
    """Migrate users from old to new database"""
    try:
        old_conn = pymysql.connect(**OLD_DB_CONFIG)
        new_conn = pymysql.connect(**NEW_DB_CONFIG)
        
        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()
        
        # Get users from old database
        old_cursor.execute("SELECT * FROM user")
        users = old_cursor.fetchall()
        
        # Get column names
        old_cursor.execute("DESCRIBE user")
        columns = [row[0] for row in old_cursor.fetchall()]
        
        migrated_count = 0
        
        for user in users:
            user_dict = dict(zip(columns, user))
            
            # Map user_type to role_id
            role_id = 1  # Default to renter
            if user_dict.get('user_type') == 'owner':
                role_id = 2
            elif user_dict.get('user_type') == 'freelancer':
                role_id = 3
            
            # Insert into new database
            new_cursor.execute("""
                INSERT IGNORE INTO users (
                    id, name, email, phone, password, role_id, profile_picture,
                    is_verified, is_active, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_dict['id'],
                user_dict['name'],
                user_dict['email'],
                user_dict['phone'],
                user_dict['password'],
                role_id,
                user_dict.get('profile_picture'),
                user_dict.get('is_verified', False),
                True,  # is_active
                user_dict.get('created_at', datetime.now()),
                user_dict.get('updated_at', datetime.now())
            ))
            
            migrated_count += 1
        
        new_conn.commit()
        print(f"✅ Migrated {migrated_count} users")
        
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error migrating users: {e}")
        return False

def migrate_categories():
    """Migrate categories from old to new database"""
    try:
        old_conn = pymysql.connect(**OLD_DB_CONFIG)
        new_conn = pymysql.connect(**NEW_DB_CONFIG)
        
        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()
        
        # Get categories from old database
        old_cursor.execute("SELECT * FROM category")
        categories = old_cursor.fetchall()
        
        # Get column names
        old_cursor.execute("DESCRIBE category")
        columns = [row[0] for row in old_cursor.fetchall()]
        
        migrated_count = 0
        
        for category in categories:
            category_dict = dict(zip(columns, category))
            
            # Check if category already exists to avoid duplicates
            new_cursor.execute("SELECT id FROM categories WHERE name = %s", (category_dict['name'],))
            if new_cursor.fetchone():
                continue  # Skip if category already exists
            
            # Insert into new database
            new_cursor.execute("""
                INSERT IGNORE INTO categories (
                    id, name, description, icon, is_active, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                category_dict['id'],
                category_dict['name'],
                category_dict.get('description'),
                category_dict.get('icon'),
                True,  # is_active
                category_dict.get('created_at', datetime.now())
            ))
            
            migrated_count += 1
        
        new_conn.commit()
        print(f"✅ Migrated {migrated_count} categories")
        
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error migrating categories: {e}")
        return False

def migrate_listings():
    """Migrate listings from old to new database"""
    try:
        old_conn = pymysql.connect(**OLD_DB_CONFIG)
        new_conn = pymysql.connect(**NEW_DB_CONFIG)
        
        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()
        
        # Get listings from old database
        old_cursor.execute("SELECT * FROM listing")
        listings = old_cursor.fetchall()
        
        # Get column names
        old_cursor.execute("DESCRIBE listing")
        columns = [row[0] for row in old_cursor.fetchall()]
        
        migrated_count = 0
        
        for listing in listings:
            listing_dict = dict(zip(columns, listing))
            
            # Handle availability field - ensure it's valid JSON
            availability = listing_dict.get('availability', '{}')
            if availability and availability != '{}':
                try:
                    # Try to parse as JSON to validate
                    import json
                    json.loads(availability)
                except:
                    # If invalid, use default empty object
                    availability = '{}'
            else:
                availability = '{}'
            
            # Insert into new database
            new_cursor.execute("""
                INSERT IGNORE INTO listings (
                    id, title, description, price, location, category_id, owner_id,
                    availability, status, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                listing_dict['id'],
                listing_dict['title'],
                listing_dict['description'],
                listing_dict['price'],
                listing_dict['location'],
                listing_dict['category_id'],
                listing_dict['owner_id'],
                availability,
                'active' if listing_dict.get('status') == 'active' else 'draft',
                listing_dict.get('created_at', datetime.now()),
                listing_dict.get('updated_at', datetime.now())
            ))
            
            # Migrate images if they exist
            if listing_dict.get('images'):
                try:
                    import json
                    images = json.loads(listing_dict['images'])
                    if isinstance(images, list) and images:
                        for i, image_url in enumerate(images):
                            new_cursor.execute("""
                                INSERT INTO listing_images (
                                    listing_id, image_url, sort_order, is_primary
                                ) VALUES (%s, %s, %s, %s)
                            """, (
                                listing_dict['id'],
                                image_url,
                                i,
                                i == 0  # First image is primary
                            ))
                except:
                    pass  # Skip if images can't be parsed
            
            migrated_count += 1
        
        new_conn.commit()
        print(f"✅ Migrated {migrated_count} listings")
        
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error migrating listings: {e}")
        return False

def migrate_bookings():
    """Migrate bookings from old to new database"""
    try:
        old_conn = pymysql.connect(**OLD_DB_CONFIG)
        new_conn = pymysql.connect(**NEW_DB_CONFIG)
        
        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()
        
        # Get bookings from old database
        old_cursor.execute("SELECT * FROM booking")
        bookings = old_cursor.fetchall()
        
        # Get column names
        old_cursor.execute("DESCRIBE booking")
        columns = [row[0] for row in old_cursor.fetchall()]
        
        migrated_count = 0
        
        for booking in bookings:
            booking_dict = dict(zip(columns, booking))
            
            # Insert into new database
            new_cursor.execute("""
                INSERT IGNORE INTO bookings (
                    id, listing_id, renter_id, start_date, end_date, total_amount,
                    security_deposit, status, payment_status, special_requests,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                booking_dict['id'],
                booking_dict['listing_id'],
                booking_dict['renter_id'],
                booking_dict['start_date'],
                booking_dict['end_date'],
                booking_dict['total_amount'],
                booking_dict.get('security_deposit', 0.00),
                booking_dict.get('status', 'pending'),
                booking_dict.get('payment_status', 'pending'),
                booking_dict.get('special_requests'),
                booking_dict.get('created_at', datetime.now()),
                booking_dict.get('updated_at', datetime.now())
            ))
            
            migrated_count += 1
        
        new_conn.commit()
        print(f"✅ Migrated {migrated_count} bookings")
        
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error migrating bookings: {e}")
        return False

def migrate_reviews():
    """Migrate reviews from old to new database"""
    try:
        old_conn = pymysql.connect(**OLD_DB_CONFIG)
        new_conn = pymysql.connect(**NEW_DB_CONFIG)
        
        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()
        
        # Get reviews from old database
        old_cursor.execute("SELECT * FROM review")
        reviews = old_cursor.fetchall()
        
        # Get column names
        old_cursor.execute("DESCRIBE review")
        columns = [row[0] for row in old_cursor.fetchall()]
        
        migrated_count = 0
        
        for review in reviews:
            review_dict = dict(zip(columns, review))
            
            # Insert into new database
            new_cursor.execute("""
                INSERT IGNORE INTO reviews (
                    id, listing_id, reviewer_id, reviewee_id, rating, comment,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                review_dict['id'],
                review_dict['listing_id'],
                review_dict['reviewer_id'],
                review_dict['reviewee_id'],
                review_dict['rating'],
                review_dict.get('comment'),
                review_dict.get('created_at', datetime.now())
            ))
            
            migrated_count += 1
        
        new_conn.commit()
        print(f"✅ Migrated {migrated_count} reviews")
        
        old_cursor.close()
        new_cursor.close()
        old_conn.close()
        new_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error migrating reviews: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting migration from RentAssured Basic to Advanced Database...")
    print("=" * 60)
    
    # Check if old database exists
    try:
        old_conn = pymysql.connect(**OLD_DB_CONFIG)
        old_conn.close()
    except:
        print("❌ Old database 'rentassured' not found or not accessible")
        print("Please ensure the old database exists and is accessible")
        sys.exit(1)
    
    # Check if new database exists
    try:
        new_conn = pymysql.connect(**NEW_DB_CONFIG)
        new_conn.close()
    except:
        print("❌ New database 'rentassured_advanced' not found")
        print("Please run setup_advanced_database.py first")
        sys.exit(1)
    
    print("✅ Both databases are accessible")
    print()
    
    # Start migration
    success = True
    
    print("📊 Migrating data...")
    print("-" * 30)
    
    if not migrate_users():
        success = False
    
    if not migrate_categories():
        success = False
    
    if not migrate_listings():
        success = False
    
    if not migrate_bookings():
        success = False
    
    if not migrate_reviews():
        success = False
    
    print("-" * 30)
    
    if success:
        print("🎉 Migration completed successfully!")
        print()
        print("📋 Migration Summary:")
        print("   • Users migrated with role mapping")
        print("   • Categories migrated")
        print("   • Listings migrated with image handling")
        print("   • Bookings migrated")
        print("   • Reviews migrated")
        print()
        print("🔄 Next Steps:")
        print("   1. Update your app.py to use the new database")
        print("   2. Test the application with the new structure")
        print("   3. Consider backing up the old database")
    else:
        print("❌ Migration completed with errors")
        print("Please check the error messages above and fix any issues")

if __name__ == "__main__":
    main()
