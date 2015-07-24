# cardDB
A command-line CRUD app that uses PostgreSQL 9.4 and Python 3.4.

Originally designed around a baseball card collection in a single table, CardDB can be easily modified for other applications. CardDB utilizes the datetime, os, psycopg2, re, and texttable libraries. It is intended for use in a shell larger than the standard Windows command prompt - Powershell works great. Resize the shell window if each returned table row does not fit on its own line.

With CardDB, you can:

- Search records by up to two column fields simultaneously
- Add records to the database
- Remove records from the database
- Modify existing records

All input is validated to provide a smooth user experience and protect against SQL injection, and exceptions are handled gracefully. While certainly not "full-featured," it is simple and functional, and always being updated and improved. I am learning Python as a first language, and so far, CardDB is my 'flagship' project.

CardDB is a written in a more 'functional' programming style, in that there are no classes. There is proably a way to write this in a more object-oriented style as well, perhaps that will be another experiment in the future.

To use this program, you must have PostgreSQL installed, and a database to hold the table that the script uses. Refer to the create_table_and_role.sql file to get the table created and enable the script to interact with it. Have fun!
