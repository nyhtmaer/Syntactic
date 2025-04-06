#!/usr/bin/env python3
"""
Test script to verify comment preservation in code transformation.
"""

import ast
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers.sugar_transformer import transform_code

def test_comment_preservation():
    """Test that comments are preserved during code transformation."""
    # Test case 1: List comprehension with comment above
    input_code = '''# This is a top comment about the list comprehension
result = []
for x in range(10):
    # This comment explains what we're doing in the loop
    result.append(x * 2)
'''
    
    print("Input code:")
    print(input_code)
    print("-" * 40)
    
    # Transform the code
    transformed_code, transformations = transform_code(input_code)
    
    print("Transformed code:")
    print(transformed_code)
    print("-" * 40)
    
    print("Applied transformations:", transformations)
    
    # Test case 2: Only comments in the code
    input_code_2 = '''# This is just a comment
# Another comment
# No code here
'''
    
    print("\nTest case 2 - Only comments:")
    print(input_code_2)
    print("-" * 40)
    
    # Transform the code
    transformed_code_2, transformations_2 = transform_code(input_code_2)
    
    print("Transformed code:")
    print(transformed_code_2)
    print("-" * 40)
    
    print("Applied transformations:", transformations_2)

if __name__ == "__main__":
    test_comment_preservation() 