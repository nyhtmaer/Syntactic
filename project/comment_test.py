#!/usr/bin/env python3
"""
Test to verify comment preservation and conciseness in the code transformation.
"""

import ast
import astunparse
from transformers.sugar_transformer import transform_code
from utils.sugar_utils import concise_comment

# Sample code with various comment styles
code_with_comments = """
# This is a comment at the top of the file that should be preserved
# This is another comment that should be preserved as well

# This is a comment explaining the creation of a list with a for-loop and append
items = [1, 2, 3, 4, 5]  # This is an inline comment that should be kept
result = []  # Initialize empty result list to store doubled values
for x in items:  # For each item in our collection
    # This comment explains that we're doubling the value and appending it
    result.append(x * 2)  # It is important to note that this doubles the value x and appends it to the result list

# This is a comment explaining that we're computing a sum
numbers = [1, 2, 3, 4, 5]  # Another inline comment
total = 0  # Initialize total to zero in order to compute the sum
for x in numbers:  # For each number in our number collection
    # This comment explains the accumulation
    total += x  # We are adding the current value to our running total
"""

def test_comment_preservation():
    """Test if comments are preserved during transformation."""
    print("Testing comment preservation and conciseness:\n")
    print("Original code:")
    print(code_with_comments)
    
    # Transform the code
    transformed_code, transformations = transform_code(code_with_comments)
    
    print("\nTransformed code (with preserved comments):")
    print(transformed_code)
    
    # Display which transformations were applied
    print("\nApplied transformations:")
    for t in transformations:
        print(f"- {t['type']} at line {t['location'][0]}")
    
    # Test the concise_comment function directly
    print("\nTesting concise_comment function directly:")
    verbose_comments = [
        "# It is important to note that we need to add these values in order to get the sum",
        "# Due to the fact that we are iterating over this list, we can simplify this with a list comprehension",
        "# For all intents and purposes, this function essentially just maps the input values to doubled values"
    ]
    
    for comment in verbose_comments:
        concise = concise_comment(comment)
        print(f"Original: {comment}")
        print(f"Concise:  {concise}")
        print()

if __name__ == "__main__":
    test_comment_preservation() 