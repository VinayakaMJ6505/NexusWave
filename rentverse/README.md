# RentAssured - Rental & Freelancing Marketplace

A comprehensive peer-to-peer marketplace platform for renting products and hiring freelancing services, built with Python Flask and MySQL.

## Features

### Core Functionality
- **User Authentication**: Registration, login, and profile management
- **Product Listings**: Create and manage rental listings
- **Service Listings**: Offer freelancing services
- **Search & Discovery**: Advanced filtering and search capabilities
- **Booking System**: Request and manage bookings
- **Review System**: Rate and review transactions
- **Payment Integration**: Secure payment processing (ready for integration)

### User Types
- **Renters**: Browse and book items/services
- **Owners**: List items for rent
- **Service Providers**: Offer freelancing services
- **Both**: Users who can both rent and list

### Categories
- Vehicles (Cars, bikes, etc.)
- Electronics (Laptops, cameras, gadgets)
- Furniture (Home and office furniture)
- Photography Services
- Home Services (Cleaning, maintenance, repairs)
- Professional Services (Consulting, tutoring, design)

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **MySQL** - Database
- **Flask-Bcrypt** - Password hashing
- **Flask-JWT-Extended** - JWT authentication

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with Bootstrap 5
- **JavaScript** - Interactive functionality
- **Bootstrap 5** - Responsive design
- **Font Awesome** - Icons

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

### Database Setup
1. Install MySQL Server
2. Create a database named `rentassured`:
   ```sql
   CREATE DATABASE rentassured;
   ```
3. Update the database connection string in `app.py`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/rentassured'
   ```

### Application Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rentassured
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
rentassured/
├── app.py                 # Main Flask application
├── models.py              # Database models (if separate)
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── register.html     # User registration
│   ├── login.html        # User login
│   ├── dashboard.html    # User dashboard
│   ├── listings.html     # Browse listings
│   ├── listing_detail.html # Individual listing
│   └── create_listing.html # Create new listing
└── static/               # Static files
    ├── css/
    │   └── style.css     # Custom styles
    ├── js/
    │   └── main.js       # JavaScript functionality
    └── images/           # Image assets
```

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /dashboard` - User dashboard (protected)

### Listings
- `GET /listings` - Browse all listings
- `GET /listing/<id>` - View specific listing
- `GET /create_listing` - Create listing form (protected)
- `POST /create_listing` - Submit new listing (protected)

### Bookings
- `POST /book_listing` - Create booking request (protected)

### Categories
- `GET /api/categories` - Get all categories

## Database Schema

### Users Table
- id, name, email, phone, password, user_type
- profile_picture, is_verified, created_at, updated_at

### Categories Table
- id, name, description, icon, created_at

### Listings Table
- id, title, description, price, location
- category_id, owner_id, images, availability, status
- created_at, updated_at

### Bookings Table
- id, listing_id, renter_id, start_date, end_date
- total_amount, security_deposit, status, payment_status
- created_at, updated_at

### Reviews Table
- id, listing_id, reviewer_id, reviewee_id
- rating, comment, created_at

## Configuration

### Environment Variables
Create a `.env` file for sensitive configuration:
```
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/rentassured
JWT_SECRET_KEY=your-jwt-secret
```

### Database Configuration
Update the database connection in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/rentassured'
```

## Features in Development

### Planned Features
- [ ] Payment gateway integration (Razorpay)
- [ ] Image upload and management
- [ ] Real-time messaging
- [ ] Mobile app (React Native)
- [ ] Advanced search with filters
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Analytics and reporting

### Security Features
- [ ] Input validation and sanitization
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] SQL injection prevention
- [ ] XSS protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact:
- Email: support@rentassured.com
- Documentation: [Link to documentation]
- Issues: [GitHub Issues]

## Roadmap

### Phase 1 (MVP) - Completed
- Basic user authentication
- Listing creation and management
- Search and browse functionality
- Basic booking system

### Phase 2 - In Progress
- Payment integration
- Image upload
- Enhanced UI/UX
- Mobile responsiveness

### Phase 3 - Planned
- Real-time messaging
- Advanced analytics
- Mobile app
- API for third-party integrations

---

**RentAssured** - India's premier rental and freelancing marketplace platform.
