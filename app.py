from flask import Flask, request, jsonify
import uuid
from math import ceil
import os
import json
app = Flask(__name__)

receipts ={}

def points_calculate(receipt):
    points = 0
    retailer = receipt['retailer']
    purchase_date = receipt['purchaseDate']
    purchase_time = receipt['purchaseTime']
    items = receipt['items']
    total = float(receipt['total'])

    # Rules Implementation

    #Rule 1 --> One point for every alphanumeric character in the retailer name.
    points+= sum(char.isalnum() for char in retailer)

    # Rule 2 --> 50 points if the total is a round dollar amount with no cents.
    if total.is_integer():
        points+=50

    # Rule 3 --> 25 points if the total is a multiple of 0.25.
    if total % 0.25 == 0:
        points+=25
    
    # Rule 4 --> 5 points for every two items on the receipt.
    points += (len(items) // 2) * 5

    # Rule 5 --> If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer.
    for item in items:
        length_of_description = len(item['shortDescription'].strip())
        if length_of_description % 3 == 0:
            points+= ceil(float(item['price']) * 0.2)

    # Rule 6 --> 6 points if the day in the purchase date is odd.
    day = int(purchase_date.split('-')[-1])
    if day % 2 != 0:
        points+=6

    # Rule 7 --> 10 points if the time of purchase is after 2:00pm and before 4:00pm.
    hour, minute = map(int, purchase_time.split(':'))
    if 14 <= hour < 16:
        points += 10

    return points
    

#Endpoint: Process Receipts

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    receipt = request.json
    receipt_id = str(uuid.uuid4())
    points = points_calculate(receipt)
    receipts[receipt_id] = points
    return jsonify({"id": receipt_id}), 200

#Endpoint: Get Points

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    points = receipts.get(receipt_id)
    if points is None:
        return jsonify({"error": "Receipt not found"}), 404
    return jsonify({"points": points}), 200
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8009)
