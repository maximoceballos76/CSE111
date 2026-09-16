"""
Author: Máximo Ceballos

Purpose: Calculate the customer discount on Tuesday or Wednesday for a retail store.
"""

from datetime import datetime
DISCOUNT_RATE = .01

# Ask user for the subtotal

subtotal = float(input("Please enter the subtotal: "))

# Get the day of the week

current_date_and_time = datetime.now()

weekday = current_date_and_time.weekday()

# Compute and print the discount amount

if weekday == 1 or weekday == 2:
    if subtotal >= 50:
        discount = subtotal * DISCOUNT_RATE
        subtotal = subtotal - discount
        print(f"Your subtotal discount is: {discount:.2f}")

print(f"your subtotal is: {subtotal:.2f}")