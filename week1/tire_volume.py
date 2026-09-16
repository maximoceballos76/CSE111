# import 

from datetime import date
import math

# inputs

width = int(input("Tire width in mm: "))
aspect = int(input("Aspect ratio: "))
diameter = int(input("Diameter of wheel in inches: "))

# Calculate

volume = (math.pi * (width**2) * aspect * (width * aspect + 2540 * diameter)) / 10000000000
today = date.today()

# Display

print(f"{today} {width} {aspect} {diameter} {volume:.2f}")

