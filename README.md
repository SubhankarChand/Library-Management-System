
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