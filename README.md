# Invitation Card Management System

A Digital Product Management API for managing Invitation Cards, built with Django REST Framework.

## Features

- **Models**: Management of Categories, Tags, Cards, and Card Images.
- **REST API**: CBVs/ViewSets for CRUD operations.
- **Image Upload**: Support for multiple image uploads with S3 integration.
- **Filtering**: Filter cards by category, tag, and title.
- **Documentation**: Swagger UI 
- **JWT Authentication**: Secure API access.
- **Admin Panel**: customized admin interface with inline image management.

## Tech Stack

- Python 3.10+
- Django 4.x
- Django Rest Framework
- SQLite (Default)
- Boto3 (AWS S3)
- drf-spectacular (Documentation)

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    - Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env  # or copy manually on Windows
        ```
    - Update `.env` with your AWS credentials if using S3.

5.  **Run Migrations:**
    ```bash
    cd invitation
    python manage.py migrate
    ```

6.  **Create Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run Dev Server:**
    ```bash
    python manage.py runserver
    ```

## API Documentation

Once the server is running, access the documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

## API Usage Examples

### Authentication
- **Get Token**: `POST /api/token/`
- **Refresh Token**: `POST /api/token/refresh/`

### Cards
- **List Cards**: `GET /api/cards/`
- **Create Card**: `POST /api/cards/` (Multipart/form-data for images)
- **Upload Images**: `POST /api/cards/{id}/upload-images/`
- **Filter**: `GET /api/cards/?category=1&title=wedding`
