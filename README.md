# Final Year eCommerce Project

This is the final year project for a personalised eCommerce web application that features:
- A product recommendation system (guest, profile-based, and behavioural)
- Static AR try-on for glasses
- Price comparison across vendors
- User authentication, dashboard, wishlist, and order tracking

## Features
- Personalised multi-layered product recommendations
- Real-time product view tracking and smart suggestions
- Price comparison with vendor links
- Augmented Reality (AR) try-on using uploaded selfies and transparent overlays
- User registration, login, profile, and dashboard
- Wishlist and basket functionality
- Admin panel for managing products and prices

## Instructions

These instructions will get your local development server running.

### Prerequisites

Ensure you have the following installed:

- **Python 3.9+**
- **pip** (Python package manager)
- **Git** (optional, for cloning)
- **Virtualenv** (recommended)

### Step-by-step Setup

1. **Clone the repository** or download the ZIP:
   ```bash
   git clone https://github.com/YuQing15/FYP-Ecommerce
   cd FYP-Ecommerce
   ```

2. **(Optional) Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser for admin access** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the app** in your browser at:
   ```
   http://127.0.0.1:8000/
   ```

## Project Structure

- `myapp/` – Main Django app (models, views, templates)
- `static/` – CSS, images, AR overlays
- `media/` – User-uploaded selfies for AR
- `templates/` – HTML templates
- `load_products.py` – Script to preload demo product data
- `update_prices.py` – Prototype scraper for vendor prices

## Admin Access

To manage users, products, and prices via the Django Admin panel:
- Visit: `http://127.0.0.1:8000/admin/`
- Login with your superuser credentials
