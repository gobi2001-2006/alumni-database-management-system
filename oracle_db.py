import oracledb

# DO NOT use init_oracle_client() for Thin mode

# Create a connection
connection = oracledb.connect(
    user="system",
    password="2006",
    dsn="localhost/XEPDB1"
)

# Use the connection
cursor = connection.cursor()
cursor.execute("SELECT sysdate FROM dual")
result = cursor.fetchone()
print("Current Oracle time:", result[0])

cursor.close()
connection.close()


