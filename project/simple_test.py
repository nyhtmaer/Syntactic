#!/usr/bin/env python3
"""
Simple test to verify the bug fixes.
"""

import ast
import astunparse
from transformers.sugar_transformer import transform_code

# 1. Building a list with a for-loop and append
list_code = """
items = [1, 2, 3, 4, 5]
result = []
for x in items:
    result.append(x * 2)
"""

# 8. Sum with a loop  
sum_code = """
numbers = [1, 2, 3, 4, 5]
total = 0
for x in numbers:
    total += x
"""

def clean_redundant_assignments(tree):
    """Simple implementation to remove redundant assignments."""
    new_body = []
    var_assignments = {}
    
    # First pass: track variables and their values
    for i, stmt in enumerate(tree.body):
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            var_name = stmt.targets[0].id
            
            # Track empty container initializations
            if (isinstance(stmt.value, ast.List) and len(stmt.value.elts) == 0 or
                isinstance(stmt.value, ast.Dict) and len(stmt.value.keys) == 0 or
                isinstance(stmt.value, ast.Num) and stmt.value.n == 0):
                
                # If we already saw this variable, skip this initialization
                if var_name in var_assignments:
                    continue
                
                var_assignments[var_name] = True
        
        new_body.append(stmt)
    
    tree.body = new_body
    return tree

def transform_list_comprehension():
    """Test transformation for list comprehension."""
    print("Testing list comprehension transformation:")
    print("Original code:")
    print(list_code)
    
    # Parse the code
    tree = ast.parse(list_code)
    
    # First pass to detect empty list initializations
    new_body = []
    result_initialized = False
    
    for stmt in tree.body:
        # Skip empty list initializations for 'result'
        if (isinstance(stmt, ast.Assign) and 
            len(stmt.targets) == 1 and 
            isinstance(stmt.targets[0], ast.Name) and 
            stmt.targets[0].id == 'result' and
            isinstance(stmt.value, ast.List) and 
            len(stmt.value.elts) == 0):
            result_initialized = True
            continue
        
        new_body.append(stmt)
    
    # Replace tree body with cleaned version
    tree.body = new_body
    
    # Second pass to transform for loops with append to list comprehensions
    for i, stmt in enumerate(tree.body):
        if isinstance(stmt, ast.For):
            # Check if body has a single append call
            if len(stmt.body) == 1 and isinstance(stmt.body[0], ast.Expr):
                expr = stmt.body[0]
                if (isinstance(expr.value, ast.Call) and 
                    isinstance(expr.value.func, ast.Attribute) and 
                    expr.value.func.attr == 'append'):
                    
                    # Get the target variable being appended to
                    target_var = expr.value.func.value.id
                    
                    # Get the expression being appended
                    value_expr = expr.value.args[0]
                    
                    # Create list comprehension
                    list_comp = ast.ListComp(
                        elt=value_expr,
                        generators=[
                            ast.comprehension(
                                target=stmt.target,
                                iter=stmt.iter,
                                ifs=[],
                                is_async=0
                            )
                        ]
                    )
                    
                    # Create replacement assignment
                    new_assign = ast.Assign(
                        targets=[ast.Name(id=target_var, ctx=ast.Store())],
                        value=list_comp
                    )
                    
                    # Replace the for loop with the list comprehension
                    tree.body[i] = new_assign
    
    # Fix missing locations
    ast.fix_missing_locations(tree)
    
    # Generate the transformed code
    transformed_code = astunparse.unparse(tree)
    print("\nTransformed code:")
    print(transformed_code)

def transform_sum():
    """Test transformation for sum pattern."""
    print("\nTesting sum transformation:")
    print("Original code:")
    print(sum_code)
    
    # Parse the code
    tree = ast.parse(sum_code)
    
    # First pass to detect initializations of 'total' to 0
    new_body = []
    total_initialized = False
    
    for stmt in tree.body:
        # Skip initializations of 'total' to 0
        if (isinstance(stmt, ast.Assign) and 
            len(stmt.targets) == 1 and 
            isinstance(stmt.targets[0], ast.Name) and 
            stmt.targets[0].id == 'total' and
            isinstance(stmt.value, ast.Num) and 
            stmt.value.n == 0):
            total_initialized = True
            continue
        
        new_body.append(stmt)
    
    # Replace tree body with cleaned version
    tree.body = new_body
    
    # Second pass to transform for loops with += to sum()
    for i, stmt in enumerate(tree.body):
        if isinstance(stmt, ast.For):
            # Check if body has a single augmented assignment
            if len(stmt.body) == 1 and isinstance(stmt.body[0], ast.AugAssign):
                aug_assign = stmt.body[0]
                
                # Check if it's adding the loop variable to 'total'
                if (isinstance(aug_assign.target, ast.Name) and 
                    aug_assign.target.id == 'total' and
                    isinstance(aug_assign.op, ast.Add)):
                    
                    # Create sum() call
                    sum_call = ast.Call(
                        func=ast.Name(id='sum', ctx=ast.Load()),
                        args=[stmt.iter],
                        keywords=[]
                    )
                    
                    # Create replacement assignment
                    new_assign = ast.Assign(
                        targets=[ast.Name(id='total', ctx=ast.Store())],
                        value=sum_call
                    )
                    
                    # Replace the for loop with the sum call
                    tree.body[i] = new_assign
    
    # Fix missing locations
    ast.fix_missing_locations(tree)
    
    # Generate the transformed code
    transformed_code = astunparse.unparse(tree)
    print("\nTransformed code:")
    print(transformed_code)

test_code = """
# Comment for list
result = []

# Comment for loop 
for x in range(10):
    # Comment for append
    result.append(x * 2)
"""

try:
    transformed, _ = transform_code(test_code)
    print("--- ORIGINAL CODE ---")
    print(test_code)
    print("--- TRANSFORMED CODE ---")
    print(transformed)
except Exception as e:
    print(f"Error: {e}")

if __name__ == "__main__":
    transform_list_comprehension()
    transform_sum() 