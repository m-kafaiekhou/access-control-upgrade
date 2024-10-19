import psycopg2

mydb = psycopg2.connect(
                host="192.168.200.1",
                user="postgres",
                password="postgres",
                database="postgres",
                port=5432
                )
                
with mydb:
        mycursor = mydb.cursor()
        
        qry="SELECT * FROM {}".format("communication")

        mycursor.execute(qry)
        myresult=mycursor.fetchone()

print(myresult)