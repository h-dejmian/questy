## questy
Web app in Python and Flask, forum in which users are able to ask questions.

# description
This application is a place where people can ask questions to the community and get answers for them. Questions can be voted up are down.
Users can register and have their accounts. In the list of users we can see number of questiones asked by every individual user, number of answers and comments to the questions.
Every user has its reputation counted based on their questions votes.

On the main page we can see few newest questions and by clicking link in the middle we can proceed to the list of all questions. Every question has answers, comments and tags,
which are added by users. Users can add tags to question by chosing them from the existing list or creating new ones. 
Editing question, answer and comment is also a possible option along with deleting all the data, but only by owners.

Only after logging in we can see all possible functions of the website, especially those related to creating, editing and deleting data.

# launch
- clone repository
- create venv
- create .env file according to schema below:
  ```
        PSQL_USER_NAME=
        PSQL_PASSWORD=
        PSQL_HOST='localhost:5432'
        PSQL_DB_NAME=
  ```
- create database in PostgreSQL with name chosen in .env file
- run sql script in sql folder

# requirements
Python==3.11.0
click==8.1.3
colorama==0.4.6      
Flask==2.2.2
itsdangerous==2.1.2  
Jinja2==3.1.2        
MarkupSafe==2.1.2    
psycopg2==2.9.5      
python-dotenv==0.21.1
Werkzeug==2.2.2


