## Step to setup MySQL database via Docker
## Some useful MySQL initial commands


## To install, run
    - brew install mysql

## To launch the service
    - brew services start mysql

## If need to run in background, can do:
    - mysql.server start
    - mysql.server stop

## To login mysql panel
    - mysql -u root -p

## Display options
    - show databases;
    - show tables;
    - use <database name>;

## To check the host of user=root, if "%", can be connected outside docker, if "localhost", can only be connected within docker
    - select user, host from mysql.user;

## others
    - update mysql.user set host='%' where user='root'
