#!/usr/bin/env python3
"""
Test script to verify comment preservation with multiple transformations.
"""

import sys
import os

# Make sure we can find the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transformers.sugar_transformer import transform_code

# Complex test with multiple transformations and comments
test_code = """
# This is a file header comment
# It should stay at the top

# Create an empty list to store results
result = []

# Loop over the range of numbers
for x in range(10):
    # Only include even numbers
    if x % 2 == 0:
        # Multiply by 2 before appending
        result.append(x * 2)

# Create a set for unique values
unique_values = set()

# Add items from the result list to the set
for item in result:
    # This adds to the set
    unique_values.add(item)

# Create a dictionary to track frequency
freq = {}

# Count occurrences of each value
for val in result:
    # Initialize if not present
    if val not in freq:
        freq[val] = 0
    # Increment the counter
    freq[val] += 1

# Get the sum using a counter
total = 0
# Loop through values to calculate sum
for val in result:
    # Add to the running total
    total += val

# Print some final information
print(f"Results: {result}")
print(f"Unique values: {unique_values}")
print(f"Frequencies: {freq}")
print(f"Total: {total}")
"""

print("Original code:")
print(test_code)

try:
    # Transform the code
    transformed, transformations = transform_code(test_code)

    print("\nTransformed code:")
    print(transformed)

    if transformations:
        print("\nApplied transformations:")
        for t in transformations:
            print(f"- {t['type']}")
    else:
        print("\nNo transformations applied")
except Exception as e:
    print(f"\nError during transformation: {e}") 