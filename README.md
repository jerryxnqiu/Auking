# First Website Project

## Technologies used:
### 1. Django
    1.1 python manage.py makemigrations
    1.2 python manage.py migrate
    1.3 python manage.py createsuperuser
        Username: admin
        Password: admin
        Email address: admin@auking.com.au
    1.4 python manage.py collectstatic
    1.5 python manage.py runserver

### 2. MySQL
#### 2.1 Install on MacOS
    2.1.1 Installation - brew install mysql
    2.1.2 To start the service - mysql.server start
    2.1.3 To stop service - brew services stop mysql/mysql.server stop
    2.1.4 Password in setting file

#### 2.2 Install on Ubuntu

### 3. Redis, as the middle layer Database
    3.1 Installation - brew install redis
    3.2 To start the service - redis-server
    3.3 To stop the service - Ctrl-C
    3.4 To retart the redis - brew services restart redis

### 4. Celery, as the delay queue for tasks
    4.1 pip install celery
    4.2 celery -A celery_tasks.tasks worker -l info

### 5. Use activation email to close the registration loop (https://www.youtube.com/watch?v=iGPPhzhXBFg)
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'example@gmail.com'
    EMAIL_HOST_PASSWORD = 'password'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

### 6. Nginx, as middle box (https://medium.com/@ThomasTan/installing-nginx-in-mac-os-x-maverick-with-homebrew-d8867b7e8a5a)
    6.1 Installation - brew install nginx
    6.2 To start the service - nginx
    6.3 To see the running message - curl HTTP://localhost:8080
    6.4 To find out the configuration file path - nginx -t
    6.5 To stop the service - nginx -s stop


### 7. Linux Ubuntu environment setup
    7.1 sudo apt-get update
    7.2 sudo apt-get upgrade
    7.3 python3 --version
    7.4 sudo apt-get install -y python3-venv

    7.5 python3 -m venv .venv




https://thenounproject.com/search/icons/?iconspage=1&q=baby%20care

https://fontawesome.com/search
