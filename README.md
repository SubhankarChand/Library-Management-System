# KitabGhar - A Modern Library Management System

## Overview

KitabGhar is a full-featured, web-based library management system built with Python and Flask. It provides a clean, modern, and intuitive interface for users, publishers, and administrators to manage a digital and physical book library.

The system features role-based access control, allowing for distinct experiences: users can browse a dynamic catalog and borrow books, publishers can manage their own book collections, and administrators have a complete overview of the library's operations.

## Key Features

### For Users

- **Welcome Page**: An engaging landing page for new visitors.

- **User Registration**: Secure account creation as either a regular user or a publisher.

- **Secure Login**: A modern, professional login page with password visibility toggle.

- **Dynamic Book Catalog**: Browse all available books with advanced filtering by category, genre, book type, and availability.

- **Book Borrowing**: Users can borrow available books with a single click.

-**Borrowing History**: A personal dashboard to view current and past borrowed books, including due dates and return status.

### For Publishers

- **Publisher Dashboard**: A dedicated dashboard with key statistics:

- Total books published.

- Total copies currently available.

- Total number of times their books have been borrowed.

- Average user rating for their books.

- **Book Management**: Easily add new books with cover images and downloadable PDFs.

- **Edit & Delete**: Full control to edit details or delete their own publications.

- **Borrowing Insights**: View a list of recent borrows for their specific books to see what's popular.

### For Administrators

- **Admin Dashboard**: A high-level overview of the entire library, including total users, total books, and currently borrowed books.

- **User Management**: (Future Scope) A panel to manage all users and publishers in the system.

## Tech Stack

### Backend

- **Framework**: Flask

- **Database ORM**: Flask-SQLAlchemy

- **Database**: MySQL (Configured via .env)

- **Migrations**: Flask-Migrate

- **Authentication**: Werkzeug Security for password hashing, Flask Sessions for session management.

### Frontend

- **Templating**: Jinja2

- **Styling**: Bootstrap 5, custom CSS for a modern look.

- **Interactivity**: Vanilla JavaScript for features like password visibility.

- **Icons**: Font Awesome

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
