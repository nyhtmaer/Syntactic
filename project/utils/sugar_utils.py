"""
Utility functions for syntactic sugar transformations.
Shared code used by parser_agent.py, sugaring_rules.py and sugar_transformer.py.
"""

import ast
import astunparse
from typing import Dict, List, Any, Tuple, Optional

# Pattern matching utilities
def match_list_comprehension(node):
    """
    Check if an AST node matches a list comprehension pattern.
    """
    # Check if the node body contains a single expression statement
    if len(node.body) != 1 or not isinstance(node.body[0], ast.Expr):
        return False
        
    # Check if the expression is a call to append
    expr = node.body[0]
    if not isinstance(expr.value, ast.Call):
        return False
        
    # Check if the call is to an attribute
    call = expr.value
    if not isinstance(call.func, ast.Attribute):
        return False
        
    # Check if the attribute is 'append'
    if call.func.attr != 'append':
        return False
        
    # Check if we have a target variable
    if not isinstance(call.func.value, ast.Name):
        return False
    
    return True

def match_set_comprehension(node):
    """
    Check if an AST node matches a set comprehension pattern.
    """
    # Check if the node body contains a single expression statement
    if len(node.body) != 1 or not isinstance(node.body[0], ast.Expr):
        return False
        
    # Check if the expression is a call to add
    expr = node.body[0]
    if not isinstance(expr.value, ast.Call):
        return False
        
    # Check if the call is to an attribute
    call = expr.value
    if not isinstance(call.func, ast.Attribute):
        return False
        
    # Check if the attribute is 'add'
    if call.func.attr != 'add':
        return False
        
    # Check if we have a target variable
    if not isinstance(call.func.value, ast.Name):
        return False
    
    return True

def match_dict_comprehension(node):
    """
    Check if an AST node matches a dict comprehension pattern.
    """
    # Check if the node body contains a single assignment
    if len(node.body) != 1 or not isinstance(node.body[0], ast.Assign):
        return False
        
    # Get the assignment node
    assign = node.body[0]
    
    # Check if assignment target is a subscript
    if len(assign.targets) != 1 or not isinstance(assign.targets[0], ast.Subscript):
        return False
        
    # Get the subscript node
    subscript = assign.targets[0]
    
    # Check if the value being subscripted is a name
    if not isinstance(subscript.value, ast.Name):
        return False
    
    return True

def match_enumerate_pattern(node):
    """
    Check if an AST node matches an enumerate pattern.
    """
    # Check if the node body contains at least one statement
    if not node.body:
        return False
        
    # Look for i += 1 or i = i + 1 pattern at the end of the loop body
    increment = node.body[-1]
    
    # Check for augmented assignment (i += 1)
    if isinstance(increment, ast.AugAssign):
        if (isinstance(increment.target, ast.Name) and 
            isinstance(increment.value, ast.Num) and 
            increment.value.n == 1 and 
            isinstance(increment.op, ast.Add)):
            return True
                
    # Check for regular assignment (i = i + 1)
    elif isinstance(increment, ast.Assign):
        if (len(increment.targets) == 1 and 
            isinstance(increment.targets[0], ast.Name) and 
            isinstance(increment.value, ast.BinOp) and 
            isinstance(increment.value.op, ast.Add) and 
            isinstance(increment.value.left, ast.Name) and 
            isinstance(increment.value.right, ast.Num) and 
            increment.value.right.n == 1 and 
            increment.targets[0].id == increment.value.left.id):
            return True
    
    return False

def match_ternary_operator(node):
    """
    Check if an AST node matches a ternary operator pattern.
    """
    # Check if we have an 'else' branch
    if not node.orelse:
        return False
        
    # Check if both the if and else bodies consist of a single assignment
    if (len(node.body) != 1 or not isinstance(node.body[0], ast.Assign) or
        len(node.orelse) != 1 or not isinstance(node.orelse[0], ast.Assign)):
        return False
        
    # Get the assignment nodes
    if_assign = node.body[0]
    else_assign = node.orelse[0]
    
    # Check if they're assigning to the same target
    if len(if_assign.targets) != 1 or len(else_assign.targets) != 1:
        return False
    
    # Get the target names as strings for comparison
    try:
        if_target = astunparse.unparse(if_assign.targets[0]).strip()
        else_target = astunparse.unparse(else_assign.targets[0]).strip()
        
        # Check if they're the same target
        return if_target == else_target
    except:
        return False

def match_generator_expression(node):
    """
    Check if a function definition node matches a generator function pattern.
    
    Example:
        def gen():
            for x in items:
                yield x + 1
    """
    # Check if the node is a function definition
    if not isinstance(node, ast.FunctionDef):
        return False
    
    # Check if function body has a single for loop
    if len(node.body) != 1 or not isinstance(node.body[0], ast.For):
        return False
    
    # Get the for loop node
    for_loop = node.body[0]
    
    # Check if the for loop body has a single yield statement
    if len(for_loop.body) != 1 or not isinstance(for_loop.body[0], ast.Expr):
        return False
    
    # Get the expression node
    expr = for_loop.body[0]
    
    # Check if the expression is a yield
    if not isinstance(expr.value, ast.Yield):
        return False
    
    return True

def match_sum_pattern(node):
    """
    Check if an AST node matches a sum computation pattern.
    
    Example:
        total = 0
        for x in numbers:
            total += x
    """
    # Check if the node body contains a single augmented assignment
    if len(node.body) != 1 or not isinstance(node.body[0], ast.AugAssign):
        return False
    
    # Check if it's an addition operation
    augassign = node.body[0]
    if not isinstance(augassign.op, ast.Add):
        return False
    
    # Check if the target is a simple variable
    if not isinstance(augassign.target, ast.Name):
        return False
    
    # Check if the value is a reference to the loop variable or a simple expression using it
    if isinstance(augassign.value, ast.Name):
        # Case: total += x
        if augassign.value.id == node.target.id:
            return True
    
    return False

def match_find_target_pattern(node):
    """
    Check if an AST node matches a find target pattern with a boolean flag.
    
    Example:
        found = False
        for x in items:
            if x == target:
                print(f"Found target: {x}")
                found = True
                break
    """
    # Need at least one if statement in the loop body
    if len(node.body) < 1 or not any(isinstance(stmt, ast.If) for stmt in node.body):
        return False
    
    # Look for the if statement
    for stmt in node.body:
        if isinstance(stmt, ast.If):
            if_stmt = stmt
            
            # Check for a boolean assignment in the if body
            has_bool_assignment = False
            has_break = False
            
            for if_body_stmt in if_stmt.body:
                # Look for assignment of True to a variable
                if isinstance(if_body_stmt, ast.Assign) and len(if_body_stmt.targets) == 1 and isinstance(if_body_stmt.targets[0], ast.Name):
                    # Handle both Python 3.8+ (Constant) and earlier (NameConstant)
                    if hasattr(ast, 'NameConstant') and isinstance(if_body_stmt.value, ast.NameConstant):
                        has_bool_assignment = if_body_stmt.value.value is True
                    elif hasattr(ast, 'Constant') and isinstance(if_body_stmt.value, ast.Constant):
                        has_bool_assignment = if_body_stmt.value.value is True
                    # For Python 3.8+, True/False are represented as Constant with boolean value
                    elif isinstance(if_body_stmt.value, ast.Constant) and isinstance(if_body_stmt.value.value, bool):
                        has_bool_assignment = if_body_stmt.value.value is True
                    
                # Look for break statement
                if isinstance(if_body_stmt, ast.Break):
                    has_break = True
            
            # If we found both the boolean assignment and break, it's a match
            if has_bool_assignment and has_break:
                return True
    
    return False

# Common functionality for error handling
def handle_code_errors(code, error):
    """
    Handle errors that occur during code parsing or transformation.
    
    Args:
        code: Original code string
        error: The exception that occurred
        
    Returns:
        Tuple containing error information and original code
    """
    if isinstance(error, SyntaxError):
        error_line = error.lineno if hasattr(error, 'lineno') else '?'
        error_col = error.offset if hasattr(error, 'offset') else '?'
        error_text = error.text.strip() if hasattr(error, 'text') and error.text else ''
        
        error_message = f"Syntax error at line {error_line}, column {error_col}: {error}\n"
        if error_text:
            error_message += f"Near: {error_text}"
            
        return f"# ERROR: {error_message}\n{code}", []
    
    elif isinstance(error, IndentationError):
        error_line = error.lineno if hasattr(error, 'lineno') else '?'
        error_message = f"Indentation error at line {error_line}: {error}"
        
        return f"# ERROR: {error_message}\n{code}", []
    
    else:
        import traceback
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc().split('\n')[-3:-1]
        
        error_info = f"Error during transformation: {error_type}: {error_message}\n"
        error_info += '\n'.join(error_traceback)
        
        return f"# ERROR: {error_info}\n{code}", []

# AST creation utilities for transformations
def create_list_comprehension(node, call):
    """
    Create a list comprehension node from a for loop with append.
    """
    elt = call.args[0]  # The argument to append becomes the list comp expression
    generators = [ast.comprehension(
        target=node.target,
        iter=node.iter,
        ifs=[],
        is_async=0
    )]
    
    # Create the list comprehension
    list_comp = ast.ListComp(elt=elt, generators=generators)
    
    # Create an assignment to the target variable
    assignment = ast.Assign(
        targets=[ast.Name(id=call.func.value.id, ctx=ast.Store())],
        value=list_comp
    )
    
    return assignment

def create_set_comprehension(node, call):
    """
    Create a set comprehension node from a for loop with add.
    """
    elt = call.args[0]  # The argument to add becomes the set comp expression
    generators = [ast.comprehension(
        target=node.target,
        iter=node.iter,
        ifs=[],
        is_async=0
    )]
    
    # Create the set comprehension
    set_comp = ast.SetComp(elt=elt, generators=generators)
    
    # Create an assignment to the target variable
    assignment = ast.Assign(
        targets=[ast.Name(id=call.func.value.id, ctx=ast.Store())],
        value=set_comp
    )
    
    return assignment

def create_generator_expression(func_node):
    """
    Create a generator expression from a generator function.
    
    Example:
        def gen():
            for x in items:
                yield x + 1
        
        ↓↓↓
        
        gen = (x + 1 for x in items)
    """
    # Get the for loop node
    for_loop = func_node.body[0]
    
    # Get the yield expression
    expr = for_loop.body[0]
    yield_expr = expr.value
    
    # Extract the yielded value
    elt = yield_expr.value
    
    # Create the generator expression
    generators = [ast.comprehension(
        target=for_loop.target,
        iter=for_loop.iter,
        ifs=[],
        is_async=0
    )]
    
    gen_expr = ast.GeneratorExp(elt=elt, generators=generators)
    
    # Create an assignment to the function name
    assignment = ast.Assign(
        targets=[ast.Name(id=func_node.name, ctx=ast.Store())],
        value=gen_expr
    )
    
    return assignment

def create_sum_expression(node, augassign):
    """
    Create a sum() expression from a for loop that computes a sum.
    
    Example:
        total = 0
        for x in numbers:
            total += x
            
        ↓↓↓
        
        total = sum(numbers)
    """
    # Get the target variable being accumulated into
    target_var = augassign.target.id
    
    # Create a call to sum() with the iterable as argument
    sum_call = ast.Call(
        func=ast.Name(id='sum', ctx=ast.Load()),
        args=[node.iter],
        keywords=[]
    )
    
    # Create an assignment to the target variable
    assignment = ast.Assign(
        targets=[ast.Name(id=target_var, ctx=ast.Store())],
        value=sum_call
    )
    
    return assignment

def create_find_target_expression(node):
    """
    Transform a loop with boolean flag and break into a more concise next/any expression.
    This function provides a placeholder for future implementation.
    """
    # For now, we'll just return the node as is - we're just identifying the pattern
    return node 

def concise_comment(comment):
    """
    Make a comment more concise while preserving its meaning.
    
    Args:
        comment: The original comment including # prefix
        
    Returns:
        A more concise version of the comment
    """
    # Remove the # and leading/trailing whitespace
    text = comment.lstrip('#').strip()
    
    # Skip if already short or empty
    if not text or len(text) < 20:
        return comment
        
    # Common verbose phrases to remove or replace
    verbose_phrases = [
        (r'in order to', 'to'),
        (r'for the purpose of', 'for'),
        (r'as a means to', 'to'),
        (r'with the goal of', 'to'),
        (r'due to the fact that', 'because'),
        (r'in spite of the fact that', 'although'),
        (r'with regard to', 'regarding'),
        (r'in reference to', 'regarding'),
        (r'it should be noted that', ''),
        (r'it is important to note that', ''),
        (r'it is necessary to', ''),
        (r'it is worth noting that', ''),
        (r'the reason why', 'why'),
        (r'this is a', 'a'),
        (r'this is an', 'an'),
        (r'there is a', 'a'),
        (r'there are', ''),
        (r'we can see that', ''),
        (r'we need to', ''),
        (r'we have to', ''),
        (r'we must', ''),
        (r'in this case', ''),
        (r'at this point in time', 'now'),
        (r'at the present time', 'now'),
        (r'at this moment', 'now'),
        (r'currently', ''),
        (r'presently', ''),
        (r'at the current time', 'now'),
        (r'for all intents and purposes', ''),
        (r'in a very real sense', ''),
        (r'basically', ''),
        (r'essentially', ''),
        (r'actually', ''),
        (r'really', ''),
        (r'definitely', ''),
        (r'certainly', ''),
        (r'absolutely', ''),
        (r'simply', ''),
        (r'just', ''),
        (r'quite', ''),
        (r'rather', ''),
        (r'somewhat', ''),
        (r'in my opinion', ''),
        (r'from my perspective', ''),
        (r'to be honest', ''),
        (r'honestly', ''),
        (r'frankly', ''),
        (r'as a matter of fact', ''),
    ]
    
    # Replace verbose phrases with concise ones
    for phrase, replacement in verbose_phrases:
        text = text.replace(phrase, replacement)
    
    # Remove repeated spaces
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Capitalize first letter if the text is not empty
    if text:
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Add back the # prefix with a space
    return '# ' + text 