# MyLineBot

## Run the project

### on VM

1. copy the .env.example to .env
```
cp .env.example .env
```
2. fulfill the setting in .env

```
CHANNEL_ACCESS_TOKEN=XXX
CHANNEL_SECRET=XXX
DB_HOST=XXX
DB_NAME=XXX
DB_USER=XXX
DB_PASS=XXX
```

3. run gunicorn service

```
gunicorn main:app –preload
```

### run on heroku

1. create an account on heroku
2. set the environment variable to herok

```
heroku config:set CHANNEL_ACCESS_TOKEN=XXX CHANNEL_SECRET=XXX DB_HOST=XXX DB_NAME=XXX DB_USER=XXX DB_PASS=XXX
```
3. deploy

## Features

### About me

1. My resume
2. A brief introduction
3. My github page

### Tools

1. High Speed Rail time table search
2. A simple todolist implementation
