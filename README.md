# Image Gallery Backend

This is a Django-based backend for an image gallery application that provides REST API endpoints for image management and gallery features.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Virtual environment (recommended)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/swetaswami378/image-gallery-backend.git
   cd image-gallery-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r image_gallery/requirements.txt
   ```

4. Create a `.env` file in the `image_gallery` directory with the following variables:
   ```
   SECRET_KEY=your-secret-key
    DEBUG=True
    POSTGRES_DB=db_name
    POSTGRES_USER=db_user
    POSTGRES_PASSWORD=user_password
    POSTGRES_HOST=db_host
    POSTGRES_PORT=5432
    POSTGRES_SCHEMA=image_gallery
    API_KEY=AI*****************
   ```

5. Set up the database:
   ```bash
   cd image_gallery
   python manage.py migrate
   ```

6. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Server

1. Make sure you're in the `image_gallery` directory and your virtual environment is activated

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

   The server will start at `http://localhost:8000`

## API Endpoints

The API will be available at `http://localhost:8000/api/`

- Admin interface: `http://localhost:8000/admin/`
- API documentation: `http://localhost:8000/api/docs/` (if configured)

## Project Structure

```
image_gallery/
├── manage.py
├── requirements.txt
├── gallery_api/          # Main application
│   ├── models.py        # Database models
│   ├── serializers.py   # API serializers
│   ├── views.py         # API views
│   └── urls.py         # API endpoints
└── image_gallery/       # Project settings
    ├── settings.py
    └── urls.py
```