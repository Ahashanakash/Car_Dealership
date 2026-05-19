# Car Dealership Web Application

A full-featured Django-based web application for managing a car dealership, including car listings, customer and seller management, reviews, transactions, and machine learning-powered price prediction.

## Features

- **Car Listings:** Browse, search, and filter cars by various attributes (brand, color, category, etc.).
- **User Roles:** Separate modules for customers, sellers, and admins with role-based dashboards.
- **Cart & Transactions:** Add cars to cart, manage purchases, and handle transactions securely.
- **Reviews:** Customers can leave reviews for cars, enhancing trust and transparency.
- **Machine Learning:** Integrated price prediction using XGBoost for car valuation.
- **REST API:** API endpoints for cars, reviews, and other resources (Django REST Framework).
- **GraphQL Support:** Schema and endpoints for flexible data queries (Graphene-Django).
- **Media Management:** Upload and manage car images, videos, and user profile photos.
- **Admin Panel:** Django admin for managing all resources.
- **Responsive UI:** Modern, mobile-friendly templates using Django templating and static assets.

## Project Structure

- `car_dealership/` – Main Django project settings and URLs
- `cars/` – Car models, views, APIs, ML integration, templates
- `customer/` – Customer models, forms, views, templates
- `seller/` – Seller models, forms, views, templates
- `profiles/` – User profile management
- `reviews/` – Review system and APIs
- `shops/` – Shop management
- `transactions/` – Transaction and order management
- `ml/` – Machine learning models and scripts
- `media/` – Uploaded images and videos
- `static/` – Static files (JS, CSS, images)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd car_dealership
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the app:**
   - Main site: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Machine Learning

- ML models for price prediction are in the `ml/` directory.
- To retrain or update models, use the scripts provided in `ml/train_xgboost_price_model.py`.

## API & GraphQL

- REST API endpoints are available for cars, reviews, etc.
- GraphQL endpoint is available at `/graphql/` (if enabled in settings).

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.


