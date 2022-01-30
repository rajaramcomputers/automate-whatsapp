from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from flask_pymongo import PyMongo
from flask_pymongo import MongoClient
from datetime import datetime
cluster = MongoClient("mongodb+srv://jai:jai@cluster0.eo1ij.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]
app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp", "")
    res = MessagingResponse()

    user = users.find_one({"number": number})

    if bool(user) == False:
        res.message("Hi, Thanks for communication to  YARF \n\n **Type** \n *1. Contact Us* \n *2. Order Snacks"
                         "\n *3 To Know our working hours* \n *4. To get our address")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Enter a valid response")
            return str(res)
        if option == 1:
            res.message("Please send email to rajaramcomputers@gmail.com")
        elif option == 2:
            res.message("You have entered *ordering mode*")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message("1. Idly \n 2. Samosa \n 3. Vadai \n 0. Go Back")
        elif option == 3:
            res.message("We work everyday from 9 am to 10 am")
        elif option == 4:
            res.message("We are in India and Oman")
        else:
            res.message("Enter a valid response")
            return str(res)
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Enter a valid response")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("**Type** \n *1. Contact Us* \n *2. Order Snacks*"
                        "\n *3 To Know our working hours* \n *4. To get our address*")
        elif 1 <= option <=3:
            cakes = ["Idly", "Samosa", "Vadai"]
            selected = cakes[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message ("Good Choice ..")
            res.message ("Enter your Address")
        else:
            res.message("Please enter the valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us!")
        res.message(f"Your order fo {selected} will be delivered in a hour")
        orders.insert_one({"number": number, "item":selected, "address": text, "date": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi, Thanks for communication to  YARF again \n\n **Type** \n *1. Contact Us* \n *2. Order Snacks"
                    "\n *3 To Know our working hours* \n *4. To get our address")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})


    return str(res)


if __name__ == "__main__":
    app.run()
