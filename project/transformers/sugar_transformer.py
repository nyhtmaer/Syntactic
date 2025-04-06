"""
Module for transforming Python AST trees to apply syntactic sugar.
"""

import ast
import astunparse
from typing import Dict, List, Any, Tuple, Optional
from utils.sugar_utils import (
    match_list_comprehension, match_set_comprehension, match_dict_comprehension,
    match_enumerate_pattern, match_ternary_operator, match_generator_expression,
    match_sum_pattern, match_find_target_pattern, create_list_comprehension,
    create_set_comprehension, create_generator_expression, create_sum_expression,
    create_find_target_expression, handle_code_errors, concise_comment
)
from transformers.redundant_assignment_cleaner import RedundantAssignmentCleaner

class SugarTransformer(ast.NodeTransformer):
    """
    AST transformer that applies syntactic sugar to Python code.
    Transforms verbose constructs into their sugared equivalents.
    """
    
    def __init__(self, rules=None):
        self.rules = rules or []
        self.transformations = []
        self.applied_rules = []  # Keeping track of which rules were applied
        self.previous_assign_nodes = {}  # Keeping track of previous assignments by variable name
        
    def visit_Assign(self, node):
        """
        Visit Assign node to track initializations and transform tuple unpacking if applicable.
        """
        # First tracking variable initializations for comprehension transformations
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            # Storing this assignment for potential removal if it's an empty container initialization
            if (isinstance(node.value, ast.List) and len(node.value.elts) == 0 or
                isinstance(node.value, ast.Dict) and len(node.value.keys) == 0 or
                isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and 
                node.value.func.id == 'set' and len(node.value.args) == 0):
                self.previous_assign_nodes[var_name] = node
        
        # Checking for tuple unpacking pattern
        unpacking = self._transform_tuple_unpacking(node)
        if unpacking:
            self.transformations.append({
                "type": "tuple_unpacking",
                "location": (node.lineno, node.col_offset)
            })
            return unpacking
        
        # Continuing with default traversal
        self.generic_visit(node)
        return node
        
    def visit_For(self, node):
        """
        Visit For node and transform list/set/dict comprehensions if applicable.
        """
        # Checking for list comprehension pattern: for loop with append
        if match_list_comprehension(node):
            # Getting the call node for the transformation
            expr = node.body[0]
            call = expr.value
            
            # Getting the target variable being appended to
            target_var = call.func.value.id
            
            # Createing the list comprehension replacement
            list_comp = create_list_comprehension(node, call)
            
            # Recording the transformation
            self.transformations.append({
                "type": "list_comprehension",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("list_comprehension")
            
            # Marking the initialization assignment for removal if we tracked it
            if target_var in self.previous_assign_nodes:
                # Replacing the initialization with "pass" to effectively remove it
                self.previous_assign_nodes.pop(target_var)
            
            return list_comp
            
        # Checking for set comprehension pattern: for loop with add
        if match_set_comprehension(node):
            # Getting the call node for the transformation
            expr = node.body[0]
            call = expr.value
            
            # Getting the target variable being appended to
            target_var = call.func.value.id
            
            # Creating the set comprehension replacement
            set_comp = create_set_comprehension(node, call)
            
            # Recording the transformation
            self.transformations.append({
                "type": "set_comprehension",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("set_comprehension")
            
            # Marking the initialization assignment for removal if we tracked it
            if target_var in self.previous_assign_nodes:
                self.previous_assign_nodes.pop(target_var)
            
            return set_comp
            
        # Checking for sum pattern: total = 0, for x in numbers: total += x
        if match_sum_pattern(node):
            # Get the augmented assignment node
            augassign = node.body[0]
            
            # Get the target variable being accumulated
            target_var = augassign.target.id
            
            # Create the sum() expression replacement
            sum_expr = create_sum_expression(node, augassign)
            
            # Record the transformation
            self.transformations.append({
                "type": "sum_pattern",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("sum_pattern")
            
            # Mark the initialization assignment for removal if we tracked it
            if target_var in self.previous_assign_nodes:
                self.previous_assign_nodes.pop(target_var)
            
            return sum_expr

        # Check for find target pattern: boolean flag with break
        if match_find_target_pattern(node):
            # This is just for identification for now, not actual transformation
            self.transformations.append({
                "type": "find_target_pattern",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("find_target_pattern")
            
            # For now, we just identify the pattern but don't transform it
            # In a full implementation, we would transform this to 'any' or 'next'
            
            # Continue with normal processing of this node
            self.generic_visit(node)
            return node
            
        # Check for dict comprehension pattern: for loop with dict assignment
        dict_comp = self._transform_dict_comprehension(node)
        if dict_comp:
            self.transformations.append({
                "type": "dict_comprehension",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("dict_comprehension")
            return dict_comp
            
        # Check for enumerate pattern: manual counter with loop
        if match_enumerate_pattern(node):
            enum_node = self._transform_enumerate(node)
            if enum_node:
                self.transformations.append({
                    "type": "enumerate_pattern",
                    "location": (node.lineno, node.col_offset)
                })
                self.applied_rules.append("enumerate_pattern")
                return enum_node
            
        # Check for zip pattern: parallel iteration
        zip_node = self._transform_zip(node)
        if zip_node:
            self.transformations.append({
                "type": "zip_pattern",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("zip_pattern")
            return zip_node
            
        # Continue with default traversal
        self.generic_visit(node)
        return node
        
    def visit_If(self, node):
        """
        Visit If node and transform ternary operators if applicable.
        """
        # Check for ternary pattern: if/else for assignment
        if match_ternary_operator(node):
            ternary = self._transform_ternary(node)
            if ternary:
                self.transformations.append({
                    "type": "ternary_operator",
                    "location": (node.lineno, node.col_offset)
                })
                self.applied_rules.append("ternary_operator")
                return ternary
            
        # Continue with default traversal
        self.generic_visit(node)
        return node
        
    def visit_Try(self, node):
        """
        Visit Try node and transform 'with' statements if applicable.
        """
        # Check for with statement pattern: try/finally with close
        with_stmt = self._transform_with_statement(node)
        if with_stmt:
            self.transformations.append({
                "type": "with_statement",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("with_statement")
            return with_stmt
            
        # Continue with default traversal
        self.generic_visit(node)
        return node
        
    def visit_FunctionDef(self, node):
        """
        Visit FunctionDef node and transform lambda if applicable.
        """
        # Check for generator function pattern
        if match_generator_expression(node):
            generator_expr = create_generator_expression(node)
            self.transformations.append({
                "type": "generator_expression",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("generator_expression")
            return generator_expr
            
        # Check for lambda pattern: simple one-liner function
        lambda_expr = self._transform_lambda(node)
        if lambda_expr:
            self.transformations.append({
                "type": "lambda_expression",
                "location": (node.lineno, node.col_offset)
            })
            self.applied_rules.append("lambda_expression")
            return lambda_expr
            
        # Continue with default traversal
        self.generic_visit(node)
        return node
        
    # These methods are now simplified by using the utility functions
    
    def _transform_dict_comprehension(self, node):
        """
        Transform a for loop with dict assignment into a dict comprehension.
        
        Example:
            result = {}
            for x in items:
                result[x] = x * 2
            
            ↓↓↓
            
            result = {x: x * 2 for x in items}
        """
        if not match_dict_comprehension(node):
            return None
            
        # Get the assignment node
        assign = node.body[0]
        
        # Get the subscript node
        subscript = assign.targets[0]
        
        # Get the target variable name
        target_var = subscript.value.id
        
        # Get the key expression (the subscript)
        key_expr = subscript.slice
        
        # In Python 3.9+, the slice is directly the expression
        # In earlier versions, it's wrapped in an Index node
        if hasattr(ast, 'Index') and isinstance(key_expr, ast.Index):
            key_expr = key_expr.value
            
        # Get the value expression (the right side of the assignment)
        value_expr = assign.value
        
        # Create a dict comprehension node
        generators = [ast.comprehension(
            target=node.target,
            iter=node.iter,
            ifs=[],
            is_async=0
        )]
        
        # Create the dict comprehension
        dict_comp = ast.DictComp(
            key=key_expr,
            value=value_expr,
            generators=generators
        )
        
        # Create an assignment to the target variable
        assignment = ast.Assign(
            targets=[ast.Name(id=target_var, ctx=ast.Store())],
            value=dict_comp
        )
        
        return assignment
        
    def _transform_enumerate(self, node):
        """
        Transform a manual counter loop into enumerate.
        
        Example:
            i = 0
            for item in items:
                print(i, item)
                i += 1
            
            ↓↓↓
            
            for i, item in enumerate(items):
                print(i, item)
        """
        # Look for i += 1 or i = i + 1 pattern at the end of the loop body
        increment = node.body[-1]
        
        # Check for the increment pattern
        counter_var = None
        
        # Check for augmented assignment (i += 1)
        if isinstance(increment, ast.AugAssign):
            counter_var = increment.target.id
                
        # Check for regular assignment (i = i + 1)
        elif isinstance(increment, ast.Assign):
            counter_var = increment.targets[0].id
        
        # Create a new for loop that uses enumerate
        # First, create the tuple target for unpacking: (i, item)
        tuple_target = ast.Tuple(
            elts=[
                ast.Name(id=counter_var, ctx=ast.Store()),
                node.target  # The original loop target
            ],
            ctx=ast.Store()
        )
        
        # Create the enumerate call
        enumerate_call = ast.Call(
            func=ast.Name(id='enumerate', ctx=ast.Load()),
            args=[node.iter],  # The original iterable
            keywords=[]
        )
        
        # Create a new for loop node
        new_for = ast.For(
            target=tuple_target,
            iter=enumerate_call,
            body=node.body[:-1],  # Exclude the increment statement
            orelse=node.orelse,
            type_comment=getattr(node, 'type_comment', None)
        )
        
        return new_for
        
    def _transform_zip(self, node):
        """Transform index-based parallel loops into zip."""
        return None  # Placeholder
        
    def _transform_ternary(self, node):
        """
        Transform if/else assignment into ternary.
        
        Example:
            if condition:
                result = value1
            else:
                result = value2
            
            ↓↓↓
            
            result = value1 if condition else value2
        """
        # Get the assignment nodes
        if_assign = node.body[0]
        else_assign = node.orelse[0]
        
        # Get the values from both assignments
        value_if = if_assign.value
        value_else = else_assign.value
        
        # Create a ternary operator (if expression) node
        ternary = ast.IfExp(
            test=node.test,
            body=value_if,
            orelse=value_else
        )
        
        # Create a new assignment with the ternary expression
        new_assign = ast.Assign(
            targets=if_assign.targets,  # Use the targets from the if branch
            value=ternary
        )
        
        return new_assign
        
    def _transform_tuple_unpacking(self, node):
        """Transform index-based tuple element access into tuple unpacking."""
        return None  # Placeholder
        
    def _transform_with_statement(self, node):
        """Transform try/finally with close into a with statement."""
        return None  # Placeholder
        
    def _transform_lambda(self, node):
        """Transform simple function into lambda."""
        return None  # Placeholder

def transform_code(code: str, rules=None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Transform Python code by applying syntactic sugar.
    
    Args:
        code: Python source code string
        rules: List of transformation rules to apply
        
    Returns:
        Tuple containing:
        - Transformed code
        - List of applied transformations
    """
    try:
        # Parse the code while capturing original comments
        original_lines = code.splitlines()
        
        # First, extract and preserve all comments with their exact line numbers
        comments = {}
        for i, line in enumerate(original_lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                comments[i] = line
        
        # If there are no transformations to apply or just comments in the code,
        # return the original code as is to preserve the comments
        if all(line.strip() == '' or line.strip().startswith('#') for line in original_lines):
            return code, []
        
        # Parse the code
        tree = ast.parse(code)
        
        # Apply transformations
        transformer = SugarTransformer(rules)
        transformed_tree = transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        
        # Clean up redundant assignments
        cleanup_transformer = RedundantAssignmentCleaner()
        cleaned_tree = cleanup_transformer.visit(transformed_tree)
        ast.fix_missing_locations(cleaned_tree)
        
        # Generate code from the transformed AST
        transformed_code = astunparse.unparse(cleaned_tree)
        
        # Now we need to reinsert comments at appropriate positions
        # The strategy is to track empty lines and comment blocks in the original code
        
        # Group comments into blocks based on consecutive line numbers
        comment_blocks = []
        current_block = []
        prev_line = -2
        
        for line_num in sorted(comments.keys()):
            if line_num == prev_line + 1:
                # Consecutive comment
                current_block.append((line_num, comments[line_num]))
            else:
                # New comment block
                if current_block:
                    comment_blocks.append(current_block)
                current_block = [(line_num, comments[line_num])]
            prev_line = line_num
        
        if current_block:
            comment_blocks.append(current_block)
        
        # Find positions of code blocks in original code
        code_positions = []
        in_code_block = False
        code_start = 0
        
        for i, line in enumerate(original_lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # This is a code line
                if not in_code_block:
                    code_start = i
                    in_code_block = True
            elif in_code_block and (not stripped or stripped.startswith('#')):
                # End of code block
                code_positions.append((code_start, i - 1))
                in_code_block = False
        
        # Handle trailing code block
        if in_code_block:
            code_positions.append((code_start, len(original_lines) - 1))
        
        # Map comment blocks to code blocks based on proximity
        comments_for_code = {}
        for comment_block in comment_blocks:
            comment_end = comment_block[-1][0]
            
            # Find the closest code block that starts after these comments
            best_distance = float('inf')
            best_code_block = None
            
            for code_start, code_end in code_positions:
                if code_start > comment_end:
                    distance = code_start - comment_end
                    if distance < best_distance:
                        best_distance = distance
                        best_code_block = (code_start, code_end)
            
            if best_code_block and best_distance <= 3:  # Increased from 2 to 3 for better matching
                key = best_code_block[0]  # Use code start as key
                if key not in comments_for_code:
                    comments_for_code[key] = []
                comments_for_code[key].extend([c[1] for c in comment_block])
            else:
                # If we can't find a code block after the comment, 
                # consider this an inline or preceding comment
                for code_start, code_end in code_positions:
                    if comment_end >= code_start and comment_end <= code_end:
                        # This comment appears within a code block
                        key = code_start
                        if key not in comments_for_code:
                            comments_for_code[key] = []
                        comments_for_code[key].extend([c[1] for c in comment_block])
                        break
                
        # Get comment blocks that appear at the top of the file
        top_comments = []
        for i, block in enumerate(comment_blocks):
            if block[0][0] <= 2:  # Consider comments within first 3 lines as top comments
                top_comments.extend([c[1] for c in block])
            elif i == 0:  # Always include the first block as top comments
                top_comments.extend([c[1] for c in block])
        
        # Now reconstruct the transformed code with comments
        transformed_lines = transformed_code.splitlines()
        final_lines = []
        
        # Add top comments first
        if top_comments:
            final_lines.extend(top_comments)
            if final_lines and transformed_lines and final_lines[-1].strip() and transformed_lines[0].strip():
                final_lines.append("")  # Add space after top comments
        
        # Extract key code patterns from original code to identify patterns in transformed code
        code_patterns = {}
        for code_start, code_end in code_positions:
            code_block = ' '.join(original_lines[code_start:code_end+1])
            # Extract significant tokens and variable names
            tokens = set()
            for token in code_block.split():
                # Remove common syntax and punctuation
                token = token.strip(",;()[]{}:.'\"")
                if token and not token.startswith('#') and len(token) > 1:
                    # Prioritize variable names and keywords
                    if token.isidentifier() or token in ("for", "if", "while", "return", "print"):
                        tokens.add(token)
            
            if tokens and code_start in comments_for_code:
                code_patterns[tuple(sorted(tokens))] = comments_for_code[code_start]
        
        # Now scan transformed code to place comments
        added_lines = set()
        added_comments = set()
        
        # First pass: Add comments to lines with strong token matches
        for i, line in enumerate(transformed_lines):
            if i in added_lines:
                continue
                
            # Check if this transformed line contains patterns from original code
            best_match_score = 0
            best_match_comments = None
            
            for tokens, comments_list in code_patterns.items():
                line_tokens = set()
                for token in line.split():
                    token = token.strip(",;()[]{}:.'\"")
                    if token and len(token) > 1:
                        line_tokens.add(token)
                
                # Calculate match score based on token overlap
                common_tokens = 0
                for token in tokens:
                    if token in line_tokens:
                        common_tokens += 1
                
                if common_tokens > 0:
                    match_score = common_tokens / max(len(tokens), 1)
                    if match_score > best_match_score:
                        best_match_score = match_score
                        best_match_comments = comments_list
            
            # If we have a good match, add the comments
            if best_match_score >= 0.5 and best_match_comments:  # 50% match threshold
                if tuple(best_match_comments) not in added_comments:
                    final_lines.extend(best_match_comments)
                    added_comments.add(tuple(best_match_comments))
            
            final_lines.append(line)
            added_lines.add(i)
        
        # Add any remaining lines
        for i, line in enumerate(transformed_lines):
            if i not in added_lines:
                final_lines.append(line)
        
        # Determine which rules were applied
        if transformer.applied_rules:
            applied_transformations = [{"type": rule_name, "original": "", "transformed": ""} 
                               for rule_name in transformer.applied_rules]
        else:
            applied_transformations = []
            # If no transformations were made, return original code to preserve all comments
            if not applied_transformations and comments:
                return code, []
                
        # Join the final lines with preserved comments
        final_code = "\n".join(final_lines)
        
        # Return both the transformed code and metadata about applied transformations
        # Also include the original comments for reference
        return final_code, applied_transformations
        
    except Exception as e:
        # On error, return the original code unchanged with an empty list of transformations
        return code, [] 