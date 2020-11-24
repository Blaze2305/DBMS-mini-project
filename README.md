# Library Management application:
This repository contains the code for the DBMS mini-projects of Dharithri M (4NI18CS121) & Pranav B (4NI18CS122).

## What is it ?:
Library management deals in management of records. The records include books which are required by different students accordingly. Maintaining these records manually becomes difficult thus we are proving such system a computerized backend. And as the number of books increases the issue of tracking and ordering becomes exponentially harder. 
We hope to find a efficient and suitable solution for this. We use Flask as a web server along with MongoDB (a NoSQL database) as a database to store the details of each book along with other documents related to the library functions such as student library card, the list of borrowed books, books out of stock etc.
The project is built at both the administrative end and the student end , and hence only the administrator(s) ( i.e. the librarian and / or others deemed fit ) are guaranteed access to the entire database , while the student is given access only to their details and their borrowed books.
Each student can login with their USN and password and this would allow for the system to keep a track of all the members and all the books associated with them.

## Features we wish to provide:
- Manage information of members
- Track information of the book lending and dues
- Manage the information of all books
- Quality control, as manual paperwork will be eliminated in this system hence human error is reduced
- Secured data, as the data is stored offsite with no access to anyone except the application
- Weekly report generation , which included data on how many books were borrowed in the week, the fines collection etc.


## How to run:
```bash
$ pip install -r requirements.txt
$ python application.py
```

    