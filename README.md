
# 📚 KitabGhar - A Modern Library Management System

KitabGhar is a **full-featured, web-based library management system** built with **Python (Flask)**.  
It provides a clean, modern, and intuitive interface for **Users, Publishers, and Administrators** to manage both **digital and physical libraries**.

---

## 🚀 Key Features

### 👤 For Users
- **Welcome Page**: Engaging landing page for new visitors.  
- **User Registration & Login**: Secure account creation with password visibility toggle.  
- **Dynamic Book Catalog**: Browse books with advanced filtering (category, genre, type, availability).  
- **Book Borrowing**: Borrow books with one click.  
- **Borrowing History**: Track current and past borrowed books with due dates and status.  

### 🏢 For Publishers
- **Publisher Dashboard** with stats:
  - 📖 Total books published  
  - 📦 Copies available  
  - 🔄 Borrow counts  
  - ⭐ Average ratings  
- **Book Management**: Add books with cover images & downloadable PDFs.  
- **Edit & Delete**: Manage publications with full control.  
- **Borrowing Insights**: See recent borrows for popularity trends.  

### 👨‍💼 For Administrators
- **Admin Dashboard**: High-level overview of total users, books, and borrowed items.  
- **User Management (Future Scope)**: Manage all users and publishers.  

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask  
- **Database ORM**: Flask-SQLAlchemy  
- **Database**: MySQL (via `.env`)  
- **Migrations**: Flask-Migrate  
- **Authentication**: Werkzeug Security + Flask Sessions  

### Frontend
- **Templating**: Jinja2  
- **Styling**: Bootstrap 5 + Custom CSS  
- **Interactivity**: Vanilla JavaScript (password toggle, etc.)  
- **Icons**: Font Awesome  

---

## ⚡ Getting Started

Follow these steps to set up **KitabGhar** on your local machine.

### ✅ Prerequisites
- Python 3.x  
- MySQL server (or another supported DB)  
- Git  

### 📥 Installation

```bash
# Clone the repository
git clone https://github.com/SubhankarChand/Library-Management-System.git
cd Library-Management-System

# Create virtual environment
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
 ```

 ### ⚙️ Database Setup

- Create a new database in MySQL (e.g., kitabghar_db).

- Create a .env file in the root folder and configure:

```bash
# Flask session secret
SESSION_SECRET="your-very-secure-secret-key"

# Database connection string
DATABASE_URL="mysql+pymysql://USER:PASSWORD@localhost:3306/kitabghar_db?charset=utf8mb4"

# CSRF secret
CSRF_SECRET="your-csrf-secret-key"
 ```
 ## Run migrations:

```bash
 flask db init       # (only first time)
 flask db migrate -m "Initial migration"
 flask db upgrade
 ```
 ## ▶️ Run Application
```bash
python app.py
  ```
- Your app will be available at: http://127.0.0.1:5000

### 📂 Application Structure

```bash
/Library-Management-System
│-- blueprints/         # Flask route blueprints (main, auth, etc.)
│-- static/             # CSS, JS, images
│   │-- css/
│   │-- js/
│   └-- images/
│-- templates/          # Jinja2 HTML templates
│-- migrations/         # Auto-generated migration scripts
│-- .gitignore          # Ignored files/folders
│-- app.py              # Main Flask app entry point
│-- extensions.py       # Flask extensions (db, login, migrate)
│-- models.py           # SQLAlchemy models
│-- requirements.txt    # Dependencies
└-- README.md           # Project documentation
```
### 🌟 Future Scope
- User & publisher management panel for admins

- Book recommendation engine (AI/ML integration)

- Notifications for due dates & reminders

### 🤝 Contributing
- Contributions are welcome! Fork this repo, create a branch, and submit a pull request.

### 📜 License
- This project is licensed under the MIT License.

### 👨‍💻 Author

Developed by [Subhankar Chand](https://github.com/SubhankarChand/Library-Management-System)
 🚀