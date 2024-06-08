import sqlite3
connection = sqlite3.connect('database.db') 
cursor = connection.cursor()
cursor.execute( 'CREATE TABLE IF NOT EXISTS Employees (hr_id TEXT, Password TEXT)') 
with open('static/cred.txt', 'r') as file:
    for line in file:
        l = line.strip().split()
        connection.execute("INSERT INTO Employees values('{a}','{b}')".format(a=l[0], b=l[1]))
connection.commit()
connection.close()