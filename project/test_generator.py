#!/usr/bin/env python3
"""
Test script to verify our generator expression transformation.
"""

import ast
import astunparse
import sys
import os

# Make sure we can find the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.sugar_utils import match_generator_expression, create_generator_expression
from transformers.sugar_transformer import transform_code

# Test code with a generator function
test_code = """
# Example generator function
def gen():
    for x in items:
        yield x + 1
"""

print("Original code:")
print(test_code)

# Parse the code
tree = ast.parse(test_code)

# Find the function node
function_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'gen':
        function_node = node
        break

if function_node:
    # Check if it matches our generator pattern
    is_generator = match_generator_expression(function_node)
    print(f"Is generator function? {is_generator}")
    
    if is_generator:
        # Create the generator expression
        generator_expr = create_generator_expression(function_node)
        
        # Create a new module with the generator expression
        new_module = ast.Module(body=[generator_expr], type_ignores=[])
        ast.fix_missing_locations(new_module)
        
        # Generate code
        transformed_code = astunparse.unparse(new_module)
        print("\nTransformed code:")
        print(transformed_code)
else:
    print("Function node not found")

# Also test using the transform_code function
print("\nUsing transform_code function:")
transformed, transformations = transform_code(test_code)
print(transformed)
if transformations:
    print("\nApplied transformations:")
    for t in transformations:
        print(f"- {t['type']}")
else:
    print("\nNo transformations applied") 