# Auking Commerce Website - First Website Project
![webArchitecture](static/images/webArchitecture.png)

### AWS S3 setup
#### 1. To setup S3 bucket
    To setup bucket policy

#### 2. To create IAM user
    To have access key
    
#### 3. To install AWS CLI
    If you have sudo permissions, you can install the AWS CLI for all users on the computer. We provide the steps in one easy to copy and paste group. See the descriptions of each line in the following steps.

    1. Download the file using the curl command. The -o option specifies the file name that the downloaded package is written to. In this example, the file is written to AWSCLIV2.pkg in the current folder.
    
    % curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"

    2. Run the standard macOS installer program, specifying the downloaded .pkg file as the source. Use the -pkg parameter to specify the name of the package to install, and the -target / parameter for which drive to install the package to. The files are installed to /usr/local/aws-cli, and a symlink is automatically created in /usr/local/bin. You must include sudo on the command to grant write permissions to those folders.

    % sudo installer -pkg ./AWSCLIV2.pkg -target /

    After installation is complete, debug logs are written to /var/log/install.log.

    3. To verify that the shell can find and run the aws command in your $PATH, use the following commands.

    % which aws
    /usr/local/bin/aws 
    % aws --version
    aws-cli/2.10.0 Python/3.11.2 Darwin/18.7.0 botocore/2.4.5

#### 4. To configure AWS credential to support auto upload of staticfiles
    aws configure
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    DEFAULT_REGION_NAME
    DEFAULT_OUTPUT_FORMAT

#### 5. To install python libraries
    pip install django-storages
    pip install boto3

#### 6. To run the "python manage.py collectstatic"
    Only static files will be collected and upload to "https://auking.s3.ap-southeast-2.amazonaws.com/static/"
    "media/" folder need manual uploading
___
___
### Technologies used and Development Environment Setup (MacOS):

### 1. Django
#### 1.1 To setup Django project and Apps
    django-admin startproject auking .
    python manage.py startapp Apps

#### 1.2 To create new migrations based on the changes you have made to your models
    python manage.py makemigrations

#### 1.3 To apply and unapply migrations 
    python manage.py migrate

#### 1.4 To create super user 
    python manage.py createsuperuser
    Username: admin
    Password: admin
    Email address: admin@auking.com.au

#### 1.5 To collect all static files into a folder specified in settings.py - STATIC_ROOT 
    python manage.py collectstatic --noinput

#### 1.6 To run development mode server 
    python manage.py runserver
___

### 2. MySQL
#### 2.1 To install Mysql 
    brew install mysql

#### 2.2 To start the service
    brew services (services in general) will restart automatically after rebooting; the other (mysql.server start) will not.
    
    brew services start mysql
    mysql.server start
    
#### 2.3 To stop service
    brew services stop mysql
    mysql.server stop

#### 2.4 To login mysql command line mode
    mysql -u root -p
    Password in setting file

#### 2.5 To display database
    show databases;
    show tables;
    use <database name>;

#### 2.6 (optional) To check the host of user=root, if "%", can be connected outside docker, if "localhost", can only be connected within docker
    select user, host from mysql.user;
    update mysql.user set host='%' where user='root'
___

### 3. Redis, as the middle layer Database
#### 3.1 Installation
    brew install redis

#### 3.2 To start the service
    redis-server

#### 3.3 To stop the service
    Ctrl-C

#### 3.4 To retart the redis
    brew services restart redis
___

### 4. Celery, as the delay queue for tasks
#### 4.1 To install the celery
    pip install celery
     
#### 4.2 To start the celery service 
    celery -A celery_tasks.tasks worker -l info
___

### 5. To use activation email to close the registration loop (https://www.youtube.com/watch?v=iGPPhzhXBFg)
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'example@gmail.com'
    EMAIL_HOST_PASSWORD = 'password'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
___

### 6. To use "elasticsearch" as the search engine for the item searching
To work with Haystack, elasticsearch >= 7, < 8 is used
#### 6.1 To install JDK
    brew install openjdk

#### 6.2 For the system Java wrappers to find this JDK, symlink it with
    sudo ln -sfn /opt/homebrew/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk

    (Seems optional)
    If you need to have openjdk first in your PATH, run:
    % echo 'export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"' >> ~/.zshrc

    For compilers to find openjdk you may need to set:
    % export CPPFLAGS="-I/opt/homebrew/opt/openjdk/include"

#### 6.3 To install elasticsearch from archive
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-darwin-x86_64.tar.gz
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-darwin-x86_64.tar.gz.sha512
    shasum -a 512 -c elasticsearch-7.17.16-darwin-x86_64.tar.gz.sha512 
    tar -xzf elasticsearch-7.17.16-darwin-x86_64.tar.gz
    cd elasticsearch-7.17.16/ 

#### 6.4 To start the elasticsearch
    ./elasticsearch-7.17.16/bin/elasticsearch

#### 6.5 To install Kibana from archive
    curl -O https://artifacts.elastic.co/downloads/kibana/kibana-7.17.16-darwin-x86_64.tar.gz
    curl https://artifacts.elastic.co/downloads/kibana/kibana-7.17.16-darwin-x86_64.tar.gz.sha512 | shasum -a 512 -c - 
    tar -xzf kibana-7.17.16-darwin-x86_64.tar.gz
    cd kibana-7.17.16-darwin-x86_64/

#### 6.6 To start the kibana
    ./kibana-7.17.16-darwin-x86_64/bin/kibana

#### 6.7 To configure security and SSL
    Set up minimal security
    Set up basic security
    Set up basic security plus HTTPS

    path for "ca_certs" needs to be updated

#### 6.8 To building the index file
    python manage.py rebuild_index
___

### 7. To run the crawling scripts and prepare the mysql dump files
scrapy files are in scrapers/ folder and images will be saved to scrapyDownloadingImages/ folder

#### 7.1 To run the scrapy scripts
    python manage.py crawl

#### 7.2 To run mysqldump commands in MacOS and save results
    mysqldump -u root -p auking <table in database auking> > ./Desktop/Auking/mysqlInitializationScripts/001_tableName.sql
___
___
### Technologies used and Development Environment Setup (MacOS using Docker Desktop):

### 1. To prepare Dockerfile for the Django Project
    1.1 To prepare "entrypoint" script for development environment
    1.2 To prepare "entrypoint" script for production environment


### 2. To prepare docker-compose.yml
    2.1 Django Container
    2.2 Celery Container
    2.3 Redis Container
    2.3 MySQL Container
    2.4 elasticsearch Container
    2.5 kibana Container

### 3. To run the mysql dump files inside MySQL container
    mysql -u <MySQL username> -p <database name> < ./mysqlInitializationScripts/001_tableName_dump.sql

___
___
### Production Environment Setup (Ubuntu + Docker Compose)
![productionArchitecture](static/images/productionArchitecture.png)

https://medium.com/@aadarshachapagain/setting-up-django-with-mysql-nginx-and-gunicorn-on-ubuntu-18-04-c23e1334a17

### 1. Docker and Docker Compose setup
https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
#### 1.1 Set up Docker's apt repository.
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

#### 1.2 Install the Docker packages.
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose


### 2. Docker and Docker Compose setup
#### 2.1 To download the repository from Github
    git clone repository
    username: Github account name
    password: Github token


### 3. To copy .env file to remote server and update EC2 IP address
#### 3.1 .env file
    To add EC2 IP address to the ALLOWED_HOSTS variable in .env
    To copy .env content over to the remote server
    sudo nano .env

#### 3.2 boost up the docker containers
    sudo docker-compose -f docker-compose.prod.yml up