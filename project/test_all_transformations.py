#!/usr/bin/env python3
"""
Test script to verify all implemented syntactic sugar transformations.
"""

import sys
import os
import ast
import astunparse
import traceback

# Make sure we can find the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transformers.sugar_transformer import transform_code, SugarTransformer
from transformers.redundant_assignment_cleaner import RedundantAssignmentCleaner

def run_test(name, code):
    """Run an individual test and handle errors."""
    print(f"\n{name}:")
    print("-" * 30)
    try:
        transformed, transformations = transform_code(code)
        print(transformed)
        if transformations:
            print("\nApplied transformations:")
            for t in transformations:
                print(f"- {t['type']}")
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return False

# Test code with various verbose constructs
verbose_code = """
# Verbose Code Example

# 1. Building a list with a for-loop and append
items = [1, 2, 3, 4, 5]
result = []
for x in items:
    result.append(x * 2)

# 2. Iterating with a manual counter
i = 0
for item in items:
    print("Index:", i, "Item:", item)
    i += 1

# 3. Constructing a dictionary with a for-loop
mapping = {}
for x in items:
    mapping[x] = x * 3

# 4. Reading a file using try-finally
f = open("data.txt", "r")
try:
    content = f.read()
finally:
    f.close()

# 5. A generator function that yields values one by one
def gen():
    for x in items:
        yield x + 1

# 6. Conditional assignment using an if-else block
condition = True
if condition:
    output = "Yes"
else:
    output = "No"

# 7. Loop with manual boolean check for finding a target value
target = 3
found = False
for x in items:
    if x == target:
        print(f"Found target: {x}")
        found = True
        break

# 8. Aggregating a sum with a loop
numbers = [1, 2, 3, 4, 5]
total = 0
for x in numbers:
    total += x
"""

print("Original verbose code:")
print(verbose_code)
print("-" * 50)

# Process each transformation individually for clarity
print("\nProcessing individual transformations:")
print("-" * 50)

# 1. List comprehension
list_code = """
items = [1, 2, 3, 4, 5]
result = []
for x in items:
    result.append(x * 2)
"""
run_test("1. List comprehension transformation", list_code)

# 2. Enumerate pattern
enum_code = """
items = [1, 2, 3, 4, 5]
i = 0
for item in items:
    print("Index:", i, "Item:", item)
    i += 1
"""
run_test("2. Enumerate transformation", enum_code)

# 3. Dict comprehension
dict_code = """
items = [1, 2, 3, 4, 5]
mapping = {}
for x in items:
    mapping[x] = x * 3
"""
run_test("3. Dict comprehension transformation", dict_code)

# 4. Ternary operator
ternary_code = """
condition = True
if condition:
    output = "Yes"
else:
    output = "No"
"""
run_test("4. Ternary operator transformation", ternary_code)

# 5. Generator expression
gen_code = """
items = [1, 2, 3, 4, 5]
def gen():
    for x in items:
        yield x + 1
"""
run_test("5. Generator expression transformation", gen_code)

# 7. Find target with boolean flag and break
find_code = """
items = [1, 2, 3, 4, 5]
target = 3
found = False
for x in items:
    if x == target:
        print(f"Found target: {x}")
        found = True
        break
"""
run_test("7. Find target transformation", find_code)

# 8. Sum with a loop
sum_code = """
numbers = [1, 2, 3, 4, 5]
total = 0
for x in numbers:
    total += x
"""
run_test("8. Sum transformation", sum_code)

# Full transformation
print("\nFull code transformation:")
print("-" * 50)

try:
    # Parse the code
    tree = ast.parse(verbose_code)
    
    # Apply transformations
    transformer = SugarTransformer()
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    
    # Add cleanup for redundant assignments
    cleanup_transformer = RedundantAssignmentCleaner()
    cleaned_tree = cleanup_transformer.visit(transformed_tree)
    ast.fix_missing_locations(cleaned_tree)
    
    # Generate code from the transformed AST
    transformed_code = astunparse.unparse(cleaned_tree)
    
    print(transformed_code)
    
    print("\nApplied transformations:")
    for t in transformer.transformations:
        print(f"- {t['type']} at line {t['location'][0]}")
        
    # Print summary of transformation types found
    transformation_types = {}
    for t in transformer.transformations:
        t_type = t["type"]
        transformation_types[t_type] = transformation_types.get(t_type, 0) + 1
    
    print("\nTransformation summary:")
    for t_type, count in transformation_types.items():
        print(f"- {t_type}: {count} transformation(s)")
        
except Exception as e:
    print(f"Error during transformation: {str(e)}")
    import traceback
    traceback.print_exc() 