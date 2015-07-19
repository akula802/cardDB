# cardDB
A command-line CRUD app that uses PostgreSQL 9.4 and Python 3.4.

CardDB is a written in a more 'functional' programming style, in that there are no classes. As time passes, the app will more likely evolve by adding and optimizing the 'operations' performed on a more-or-less fixed set of 'things' (so classes ar not that useful anyways). There is proably a way to write this in a more object-oriented style as well, perhaps that will be another experiment in the future.

Originally designed around a baseball card collection, CardDB can be easily modified for other applications. Utilizes the datetime, os, psycopg2, re, and texttable libraries. Intended for use in a shell larger than the standard Windows command prompt - Powershell works great. Resize the shell window if each returned table row does not fit on its own line.

To use this program, you must have PostgreSQL installed, and a database to hold the table that the script uses. Refer to the create_table_and_role.sql file to get the table created and enable the script to interact with it. Have fun!
