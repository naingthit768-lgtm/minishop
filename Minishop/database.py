from pymongo import MongoClient

client = MongoClient("mongodb+srv://naingthit768_db_user:myatlas2627ts@cluster0.hijhhzr.mongodb.net/?appName=Cluster0")

db = client["minishop"]

products = db["products"]
cart = db["cart"]

try:
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas!")
    print("Database:", db.name)

except Exception as e:
    print("❌ Connection failed:")
    print(e)