# RentAssured - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

### Step 1: Database Setup
1. **Install MySQL Server** (if not already installed)
2. **Start MySQL service**
3. **Create the database**:
   ```sql
   CREATE DATABASE rentassured;
   ```
4. **Update database credentials** in `app.py` (line 14):
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://your_username:your_password@localhost/rentassured'
   ```


### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database (Optional)
Run the database setup script to create tables and sample data:
```bash
python setup_database.py
```

### Step 4: Start the Application
```bash
python run.py
```
Or directly:
```bash
python app.py
```

### Step 5: Access the Application
Open your browser and go to: `http://localhost:5000`

## 🎯 Quick Test

1. **Register a new account** at `/register`
2. **Login** at `/login`
3. **Create a listing** from the dashboard
4. **Browse listings** at `/listings`
5. **Make a booking** from any listing detail page

## 📁 Project Structure

```
rentassured/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── run.py                # Application runner
├── setup_database.py     # Database setup script
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── STARTUP_GUIDE.md     # This file
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── listings.html
│   ├── listing_detail.html
│   └── create_listing.html
└── static/              # Static files
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── images/
        └── placeholder.jpg
```

## 🔧 Configuration

### Database Configuration
Update the database connection string in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/rentassured'
```

### Security Configuration
For production, update these values in `app.py`:
```python
app.config['SECRET_KEY'] = 'your-secure-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-secure-jwt-secret'
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL is running
   - Check database credentials
   - Verify database 'rentassured' exists

2. **Module Not Found Error**
   - Run: `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or kill the process using port 5000

4. **Permission Denied**
   - Run with appropriate permissions
   - Check file/folder permissions

### Getting Help
- Check the README.md for detailed documentation
- Review error messages in the console
- Ensure all dependencies are installed

## 🎉 Success!

If everything is working correctly, you should see:
- ✅ Database connection successful
- ✅ Database tables created/verified
- ✅ Application ready!
- 🌐 Starting Flask development server...
- 📍 Application URL: http://localhost:5000

## Next Steps

1. **Customize the application** for your needs
2. **Add payment integration** (Razorpay, etc.)
3. **Implement image upload** functionality
4. **Add email notifications**
5. **Deploy to production**

---

**Happy Coding! 🚀**
