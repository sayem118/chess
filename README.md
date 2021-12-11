# Team *enter team name here* Small Group project

## Team members
The members of the team are:
- *Sayem Ahmed*
- *Cheung Fung Wilson Mak*
- *Aaron Gomes*
- *Berke Muftuoglu*
- *Alexandru Matei*

The following describes any code which has been reused
- The majority of the code has taken inspiration from the lectures and source code provided from the module 5CCS2SEG

## Project structure
The project is called `system`.  It currently consists of a single app `clubs`.

## Deployed version of the application
-The deployed version of the application can be found at [URL](https://sleepy-bayou-75745.herokuapp.com/ ).
-The admin page can be found at [URL](https://sleepy-bayou-75745.herokuapp.com/admin).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

The following describes any code which has been reused
- The majority of the code has taken inspiration from the lectures and source code provided from the module 5CCS2SEG
