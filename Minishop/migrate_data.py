from pymongo import MongoClient

# Connect to LOCAL MongoDB
local_client = MongoClient("mongodb://localhost:27017/")
local_db = local_client["minishop"]

# Connect to MongoDB Atlas
ATLAS_URI = "mongodb+srv://naingthit768_db_user:myatlas2627ts@cluster0.hijhhzr.mongodb.net/?appName=Cluster0"

atlas_client = MongoClient(ATLAS_URI)
atlas_db = atlas_client["minishop"]

# Get products from local MongoDB
products = list(local_db["products"].find())

# Copy products to Atlas
if products:
    atlas_db["products"].insert_many(products)
    print(f"Successfully copied {len(products)} products!")
else:
    print("No products found!")
