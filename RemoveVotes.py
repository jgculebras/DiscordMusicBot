import mysql.connector

user = ""
password = ""

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='botDiscord',
                                         user=user,
                                         password=password)

    cursor = connection.cursor()

    mysql_update_query = """UPDATE userVote SET voted = %s"""

    record = (0,)

    cursor.execute(mysql_update_query, record)

    connection.commit()

except mysql.connector.Error as error:
    print("Error in remove fav sql", error)


finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
