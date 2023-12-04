## Step to setup MySQL database via Docker
## Some useful MySQL initial commands


## To install, run
```sql
- brew install mysql
```

## To launch the service
```sql
- brew services start mysql
```

## If need to run in background, can do:
```sql
- mysql.server start
- mysql.server stop
```

## Display options
```sql
- show databases;
- show tables;
- use <database name>;
```

## To check the host of user=root, if "%", can be connected outside docker, if "localhost", can only be connected within docker
```sql
- select user, host from mysql.user;
```

## others
```sql
- update mysql.user set host='%' where user='root'
- mysql -u root -p
```
