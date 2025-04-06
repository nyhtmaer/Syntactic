"""
Utility functions for desugarizing Python code.
Functions to expand concise code into more verbose form and generate explanatory comments.
"""

import ast
import astunparse
import re
from typing import Dict, List, Any, Tuple, Optional

def generate_comment(node, context=""):
    """
    Generate a descriptive comment for a code node based on its structure and purpose.
    
    Args:
        node: AST node to generate comment for
        context: Optional context information for better comment generation
        
    Returns:
        A string comment with # prefix
    """
    comment = "# "
    
    # Handle different types of nodes
    if isinstance(node, ast.FunctionDef):
        comment += f"Function that {node.name.replace('_', ' ')} "
        if node.args.args:
            args = [arg.arg for arg in node.args.args]
            comment += f"using {', '.join(args)}. Functions encapsulate reusable blocks of code."
        else:
            comment += f". Functions encapsulate reusable blocks of code."
    
    elif isinstance(node, ast.ClassDef):
        comment += f"Class representing a {node.name.replace('_', ' ')}"
        if node.bases:
            bases = [astunparse.unparse(base).strip() for base in node.bases]
            comment += f", inheriting from {', '.join(bases)}. Classes are blueprints for creating objects."
        else:
            comment += f". Classes are blueprints for creating objects."
    
    elif isinstance(node, ast.Assign):
        if len(node.targets) == 1:
            target = astunparse.unparse(node.targets[0]).strip()
            value_type = type(node.value).__name__.replace('ast.', '')
            comment += f"Initialize {target} with a {value_type.lower()}. Variables store data that can be referenced later."
    
    elif isinstance(node, ast.For):
        target = astunparse.unparse(node.target).strip()
        iter_expr = astunparse.unparse(node.iter).strip()
        comment += f"Loop through each {target} in {iter_expr}. For loops iterate through collections of items."
    
    elif isinstance(node, ast.If):
        condition = astunparse.unparse(node.test).strip()
        comment += f"Check if {condition}. Conditional statements control program flow based on boolean expressions."
    
    elif isinstance(node, ast.ListComp):
        comment += "Create list using list comprehension. List comprehensions concisely build lists by applying an expression to each item in an iterable."
    
    elif isinstance(node, ast.DictComp):
        comment += "Create dictionary using dict comprehension. Dictionary comprehensions efficiently build dictionaries by applying key:value expressions to iterables."
    
    elif isinstance(node, ast.SetComp):
        comment += "Create set using set comprehension. Set comprehensions build sets of unique elements from iterables."
    
    elif isinstance(node, ast.GeneratorExp):
        comment += "Create generator expression for iterating values. Generators produce items one at a time and are memory efficient."
    
    elif isinstance(node, ast.Return):
        if node.value:
            value_desc = astunparse.unparse(node.value).strip()
            comment += f"Return {value_desc}. Return statements pass values back from functions to their callers."
        else:
            comment += "Return from function. Return statements exit a function and optionally return a value."
    
    elif isinstance(node, ast.With):
        comment += "Use context manager to handle resource cleanup automatically. With statements ensure resources are properly managed."
    
    elif isinstance(node, ast.Try):
        comment += "Handle potential errors with try-except block. Exception handling prevents program crashes by catching errors."
    
    elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
        comment += "Import necessary modules or functions. Imports allow reuse of code from other modules."
    
    else:
        # Generic fallback based on type
        node_type = type(node).__name__.replace('ast.', '')
        comment += f"{node_type} operation"
    
    # Add context if provided
    if context:
        comment += f" - {context}"
    
    return comment

def expand_list_comprehension(node):
    """
    Expand a list comprehension into a for loop with append.
    
    Args:
        node: ListComp node to expand
        
    Returns:
        AST nodes representing the expanded code
    """
    # Extract key components from the list comprehension
    target_str = astunparse.unparse(node.generators[0].target).strip()
    iter_str = astunparse.unparse(node.generators[0].iter).strip()
    element_str = astunparse.unparse(node.elt).strip()
    
    # Build a comment showing what the expanded code would look like
    comment = "# Expanded list comprehension:\n"
    comment += f"# result_list = []\n"
    comment += f"# for {target_str} in {iter_str}:\n"
    
    if node.generators[0].ifs:
        condition_str = astunparse.unparse(node.generators[0].ifs[0]).strip()
        comment += f"#     if {condition_str}:\n"
        comment += f"#         result_list.append({element_str})\n"
    else:
        comment += f"#     result_list.append({element_str})\n"
    
    # Add educational information
    comment += "#\n# List comprehensions create lists by iterating over an iterable and optionally filtering elements.\n"
    comment += "# They are more concise and often faster than equivalent for loops.\n"
    
    # Create a string literal node with the comment
    comment_node = ast.Expr(value=ast.Str(s=comment))
    
    return [comment_node]

def expand_ternary_operator(node):
    """
    Expand a ternary operator (x if condition else y) into an if-else statement.
    
    Args:
        node: IfExp node to expand
        
    Returns:
        AST nodes representing the expanded code
    """
    # Create a variable to hold the result
    result_var = ast.Name(id='result', ctx=ast.Store())
    
    # Create the if branch assignment
    if_assign = ast.Assign(
        targets=[result_var],
        value=node.body
    )
    
    # Create the else branch assignment
    else_assign = ast.Assign(
        targets=[result_var],
        value=node.orelse
    )
    
    # Create the if statement
    if_stmt = ast.If(
        test=node.test,
        body=[if_assign],
        orelse=[else_assign]
    )
    
    return [if_stmt]

def expand_generator_expression(node):
    """
    Expand a generator expression into a generator function.
    
    Args:
        node: GeneratorExp node to expand
        
    Returns:
        AST nodes representing the expanded code
    """
    # Extract key components from the generator expression
    target_str = astunparse.unparse(node.generators[0].target).strip()
    iter_str = astunparse.unparse(node.generators[0].iter).strip()
    element_str = astunparse.unparse(node.elt).strip()
    
    # Build a comment showing what the expanded code would look like
    comment = "# Generator function equivalent:\n"
    comment += "# def generate_items():\n"
    comment += f"#     for {target_str} in {iter_str}:\n"
    
    if node.generators[0].ifs:
        condition_str = astunparse.unparse(node.generators[0].ifs[0]).strip()
        comment += f"#         if {condition_str}:\n"
        comment += f"#             yield {element_str}\n"
    else:
        comment += f"#         yield {element_str}\n"
    
    # Add educational information
    comment += "#\n# Generator expressions produce values one at a time, saving memory when working with large datasets.\n"
    comment += "# Unlike lists, they don't store all values in memory at once, making them more efficient for large sequences.\n"
    
    # Create a string literal node with the comment
    comment_node = ast.Expr(value=ast.Str(s=comment))
    
    return [comment_node]

def get_educational_explanation(pattern_type):
    """
    Get an educational explanation for a specific code pattern.
    
    Args:
        pattern_type: String identifying the pattern type
        
    Returns:
        String with educational explanation
    """
    explanations = {
        "list_comprehension": """
# List comprehensions create new lists by applying an expression to each item in an iterable.
# They are more concise and often more readable than equivalent for loops.
# Basic syntax: [expression for item in iterable if condition]
# - The expression defines what goes into the new list
# - The for clause specifies the source items
# - The optional if clause filters elements
""",
        "set_comprehension": """
# Set comprehensions create sets (collections of unique elements) from iterables.
# They eliminate duplicates automatically and are useful for removing redundant data.
# Basic syntax: {expression for item in iterable if condition}
# - Curly braces {} indicate a set (not a dictionary)
# - Elements are automatically deduplicated
""",
        "dict_comprehension": """
# Dictionary comprehensions create dictionaries from iterables.
# They provide a concise way to transform and filter key-value pairs.
# Basic syntax: {key_expr: value_expr for item in iterable if condition}
# - Each iteration produces a key-value pair
# - If a key appears multiple times, the last value wins
""",
        "ternary_operator": """
# The ternary (conditional) operator provides a one-line shorthand for if-else statements.
# It evaluates one expression if the condition is true and another if it's false.
# Syntax: value_if_true if condition else value_if_false
# - More concise than a full if-else block for simple conditions
""",
        "generator_expression": """
# Generator expressions create iterators that produce values on demand.
# Unlike lists, they don't store all values in memory at once.
# Basic syntax: (expression for item in iterable if condition)
# - Parentheses () indicate a generator
# - Values are generated one at a time as needed
# - Excellent for processing large data sets with minimal memory
""",
        "enumerate_pattern": """
# The enumerate function pairs each item in an iterable with its index.
# It's useful when you need both the element and its position.
# Syntax: enumerate(iterable, start=0)
# - Returns (index, item) pairs
# - The start parameter lets you specify the initial index (defaults to 0)
""",
    }
    
    return explanations.get(pattern_type, "# This code pattern is a more verbose alternative to Python's concise syntax.") 