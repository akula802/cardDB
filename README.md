# cardDB
A command-line CRUD app that uses PostgreSQL and Python 3.

Originally designed around a baseball card collection, it can be easily modified for other applications.
Utilizes the datetime, os, psycopg2, re, and texttable libraries. Intended for use in a shell larger than
the standard Windows command prompt - Powershell works great. Resize the shell window if each returned table 
row does not fit on its own line.

To use this program, you must have PostgreSQL installed, and a database to hold the table that the script uses.
Refer to the create_table_and_roles.sql file to get the table created and enable the script to interact with
it. Have fun!
