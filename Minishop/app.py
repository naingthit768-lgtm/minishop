from flask import Flask, render_template, request, redirect
from database import products, cart

app = Flask(__name__)


# Home page
@app.route("/")
def home():
    product_list = list(products.find({}, {"_id": 0}))

    return render_template(
        "index.html",
        products=product_list
    )


# Add product to cart
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():

    product_id = int(request.form["product_id"])

    product = products.find_one({
        "product_id": product_id
    })

    # Check stock
    if product["stock"] <= 0:
        return "Sorry, this product is out of stock!"

    # Check if product is already in cart
    existing_item = cart.find_one({
        "product_id": product_id
    })

    if existing_item:

        # Increase cart quantity
        cart.update_one(
            {"product_id": product_id},
            {"$inc": {"quantity": 1}}
        )

    else:

        # Add new product to cart
        cart.insert_one({
            "product_id": product["product_id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": 1
        })

    # Reduce product stock by 1
    products.update_one(
        {"product_id": product_id},
        {"$inc": {"stock": -1}}
    )

    return redirect("/cart")


# View cart
@app.route("/cart")
def view_cart():

    cart_items = list(cart.find({}, {"_id": 0}))

    # Calculate total price of all products in cart
    cart_total = sum(
        item["price"] * item["quantity"]
        for item in cart_items
    )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        cart_total=cart_total
    )


# Update quantity
@app.route("/update-cart", methods=["POST"])
def update_cart():

    product_id = int(request.form["product_id"])
    new_quantity = int(request.form["quantity"])

    # Find current cart item
    cart_item = cart.find_one({
        "product_id": product_id
    })

    if cart_item:

        old_quantity = cart_item["quantity"]

        # Difference between new and old quantity
        difference = new_quantity - old_quantity

        # If quantity increases, check stock
        if difference > 0:

            product = products.find_one({
                "product_id": product_id
            })

            if product["stock"] < difference:
                return "Not enough stock!"

            # Reduce stock
            products.update_one(
                {"product_id": product_id},
                {"$inc": {"stock": -difference}}
            )

        # If quantity decreases, return stock
        elif difference < 0:

            products.update_one(
                {"product_id": product_id},
                {"$inc": {"stock": -difference}}
            )

        # Update cart quantity
        cart.update_one(
            {"product_id": product_id},
            {"$set": {"quantity": new_quantity}}
        )

    return redirect("/cart")


# Remove product from cart
@app.route("/remove-from-cart", methods=["POST"])
def remove_from_cart():

    product_id = int(request.form["product_id"])

    # Find the cart item first
    cart_item = cart.find_one({
        "product_id": product_id
    })

    if cart_item:

        quantity = cart_item["quantity"]

        # Return the quantity back to stock
        products.update_one(
            {"product_id": product_id},
            {"$inc": {"stock": quantity}}
        )

        # Remove from cart
        cart.delete_one({
            "product_id": product_id
        })

    return redirect("/cart")

@app.route("/stats")
def stats():

    category_stats = list(products.aggregate([
        {
            "$group": {
                "_id": "$category",
                "product_count": {"$sum": 1},
                "average_price": {"$avg": "$price"}
            }
        },
        {
            "$sort": {
                "average_price": -1
            }
        }
    ]))

    return render_template(
        "stats.html",
        category_stats=category_stats
    )

if __name__ == "__main__":  
    app.run(debug=True)