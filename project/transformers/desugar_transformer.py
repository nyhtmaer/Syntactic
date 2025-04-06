"""
Module for transforming Python AST trees to expand syntactic sugar.
This module does the opposite of sugar_transformer.py - it converts concise code into more verbose forms
and adds explanatory comments.
"""

import ast
import astunparse
import re
from typing import Dict, List, Any, Tuple, Optional
from utils.desugar_utils import (
    generate_comment,
    expand_list_comprehension,
    expand_ternary_operator,
    expand_generator_expression,
    get_educational_explanation
)


class DesugarTransformer(ast.NodeTransformer):
    """
    AST transformer that expands syntactic sugar in Python code.
    Transforms concise constructs into their more verbose equivalents.
    """
    
    def __init__(self, comment_density=0.3, input_comments=None):
        self.transformations = []
        self.comment_density = comment_density  
        self.comment_count = 0
        self.node_count = 0
        self.input_comments = input_comments or {} 
        self.enhanced_comments = {}  
    def visit(self, node):
        """
        Override to track visited nodes and potentially add comments.
        """
        self.node_count += 1
        should_add_comment = (self.comment_count / max(1, self.node_count)) < self.comment_density
        
        if should_add_comment and hasattr(node, 'lineno') and not isinstance(node, (ast.Expr, ast.Num, ast.Str)):
            comment_node = self._generate_comment_node(node)
            if comment_node:
                self.comment_count += 1
                setattr(node, 'desugar_comment', comment_node)
        
        return super().visit(node)
        
    def _generate_comment_node(self, node):
        """Generate a comment for a given node if appropriate."""
        # Skipping nodes that don't need comments
        if isinstance(node, (ast.Import, ast.ImportFrom)) and not node.names:
            return None
        
        original_comment = None
        if hasattr(node, 'lineno'):
            original_comment = self.input_comments.get(node.lineno - 1) or self.input_comments.get(node.lineno)
        
        if original_comment:
            enhanced_comment = self._enhance_original_comment(original_comment, node)
            return enhanced_comment
        
        context = ""
        if isinstance(node, ast.FunctionDef) and node.returns:
            context = f"returns {astunparse.unparse(node.returns).strip()}"
            
        return generate_comment(node, context)
    
    def _enhance_original_comment(self, original_comment, node):
        """
        Enhance an original comment with additional explanation.
        
        Args:
            original_comment: The original comment string
            node: The AST node the comment relates to
            
        Returns:
            Enhanced comment string
        """
        if isinstance(node, ast.FunctionDef):
            return f"# Function '{node.name}' - Functions organize code into reusable blocks that perform specific tasks"
                
        elif isinstance(node, ast.ClassDef):
            return f"# Class '{node.name}' - Classes are blueprints for creating objects with data and behavior"
                
        elif isinstance(node, ast.Assign):
            if len(node.targets) == 1:
                target = astunparse.unparse(node.targets[0]).strip()
                return f"# Assignment to '{target}' - Variables store values that can be referenced later in the code"
                
        elif isinstance(node, ast.For):
            target = astunparse.unparse(node.target).strip()
            iter_expr = astunparse.unparse(node.iter).strip()
            return f"# For loop iterating '{target}' over '{iter_expr}' - Loops allow executing code repeatedly for each item"
                
        elif isinstance(node, ast.If):
            condition = astunparse.unparse(node.test).strip()
            return f"# Conditional check for '{condition}' - Conditions control which code blocks execute based on a test"
                
        elif isinstance(node, ast.ListComp):
            return "# List comprehension - A concise way to create lists by applying an expression to each item in an iterable"
                
        elif isinstance(node, ast.SetComp):
            return "# Set comprehension - A concise way to create sets with unique elements derived from an iterable"
                
        elif isinstance(node, ast.DictComp):
            return "# Dictionary comprehension - A concise way to create key-value pairs from an iterable"
                
        elif isinstance(node, ast.GeneratorExp):
            return "# Generator expression - Creates an iterator that produces values lazily to save memory"
                
        elif isinstance(node, ast.Return):
            return "# Return statement - Sends a value back from a function to the caller"
                
        return generate_comment(node)
    
    def visit_ListComp(self, node):
        """
        Visit ListComp node and transform it to a for loop with append.
        """
        self.generic_visit(node)
        expanded = expand_list_comprehension(node)
        
        edu_explanation = get_educational_explanation("list_comprehension")
        expanded.append(ast.Expr(value=ast.Str(s=edu_explanation)))
        
        self.transformations.append({
            "type": "list_comprehension_expansion",
            "location": getattr(node, 'lineno', 0)
        })
        return expanded
        
    def visit_SetComp(self, node):
        """
        Visit SetComp node and transform it to a for loop with add.
        """
        self.generic_visit(node)
        
        result_var = ast.Name(id='result_set', ctx=ast.Store())
        
        init = ast.Assign(
            targets=[result_var],
            value=ast.Call(
                func=ast.Name(id='set', ctx=ast.Load()),
                args=[],
                keywords=[]
            )
        )
        
        target = node.generators[0].target
        iter_expr = node.generators[0].iter
        
        if_test = None
        if node.generators[0].ifs:
            if_test = node.generators[0].ifs[0]
        
        add_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='result_set', ctx=ast.Load()),
                attr='add',
                ctx=ast.Load()
            ),
            args=[node.elt],
            keywords=[]
        )
        
        if if_test:
            body = [ast.If(
                test=if_test,
                body=[ast.Expr(value=add_call)],
                orelse=[]
            )]
        else:
            body = [ast.Expr(value=add_call)]
        
        for_loop = ast.For(
            target=target,
            iter=iter_expr,
            body=body,
            orelse=[]
        )
        
        return_stmt = ast.Return(
            value=ast.Name(id='result_set', ctx=ast.Load())
        )
        
        edu_explanation = get_educational_explanation("set_comprehension")
        comment_node = ast.Expr(value=ast.Str(s=edu_explanation))
        
        self.transformations.append({
            "type": "set_comprehension_expansion",
            "location": getattr(node, 'lineno', 0)
        })
        
        return [comment_node, init, for_loop, return_stmt]
        
    def visit_DictComp(self, node):
        """
        Visit DictComp node and transform it to a for loop with dictionary assignment.
        """
        self.generic_visit(node)
        
        result_var = ast.Name(id='result_dict', ctx=ast.Store())
        
        init = ast.Assign(
            targets=[result_var],
            value=ast.Dict(keys=[], values=[])
        )
        
        target = node.generators[0].target
        iter_expr = node.generators[0].iter
        
        if_test = None
        if node.generators[0].ifs:
            if_test = node.generators[0].ifs[0]
        
        dict_assign = ast.Assign(
            targets=[
                ast.Subscript(
                    value=ast.Name(id='result_dict', ctx=ast.Load()),
                    slice=node.key,
                    ctx=ast.Store()
                )
            ],
            value=node.value
        )
        
        if if_test:
            body = [ast.If(
                test=if_test,
                body=[dict_assign],
                orelse=[]
            )]
        else:
            body = [dict_assign]
        
        for_loop = ast.For(
            target=target,
            iter=iter_expr,
            body=body,
            orelse=[]
        )
        
        return_stmt = ast.Return(
            value=ast.Name(id='result_dict', ctx=ast.Load())
        )
        
        edu_explanation = get_educational_explanation("dict_comprehension")
        comment_node = ast.Expr(value=ast.Str(s=edu_explanation))
        
        self.transformations.append({
            "type": "dict_comprehension_expansion",
            "location": getattr(node, 'lineno', 0)
        })
        
        return [comment_node, init, for_loop, return_stmt]
        
    def visit_IfExp(self, node):
        """
        Visit IfExp node and transform it to an if-else statement.
        """
        self.generic_visit(node)
        expanded = expand_ternary_operator(node)
        
        edu_explanation = get_educational_explanation("ternary_operator")
        comment_node = ast.Expr(value=ast.Str(s=edu_explanation))
        expanded.insert(0, comment_node)
        
        self.transformations.append({
            "type": "ternary_operator_expansion",
            "location": getattr(node, 'lineno', 0)
        })
        return expanded
        
    def visit_GeneratorExp(self, node):
        """
        Visit GeneratorExp node and transform it to a generator function.
        """
        self.generic_visit(node)
        expanded = expand_generator_expression(node)
        
        edu_explanation = get_educational_explanation("generator_expression")
        expanded.append(ast.Expr(value=ast.Str(s=edu_explanation)))
        
        self.transformations.append({
            "type": "generator_expression_expansion",
            "location": getattr(node, 'lineno', 0)
        })
        return expanded
        
    def visit_Call(self, node):
        """
        Visit Call node and transform certain function calls to more verbose alternatives.
        """
        self.generic_visit(node)
        
        if (isinstance(node.func, ast.Name) and node.func.id == 'enumerate' and len(node.args) >= 1):
            self.transformations.append({
                "type": "enumerate_expansion",
                "location": getattr(node, 'lineno', 0)
            })
            
        elif (isinstance(node.func, ast.Name) and node.func.id == 'sum' and len(node.args) >= 1):
            collection = node.args[0]
            
            init = ast.Assign(
                targets=[ast.Name(id='total', ctx=ast.Store())],
                value=ast.Num(n=0)
            )
            
            for_loop = ast.For(
                target=ast.Name(id='item', ctx=ast.Store()),
                iter=collection,
                body=[
                    ast.AugAssign(
                        target=ast.Name(id='total', ctx=ast.Store()),
                        op=ast.Add(),
                        value=ast.Name(id='item', ctx=ast.Load())
                    )
                ],
                orelse=[]
            )
            
            return_stmt = ast.Return(
                value=ast.Name(id='total', ctx=ast.Load())
            )
            
            self.transformations.append({
                "type": "sum_expansion",
                "location": getattr(node, 'lineno', 0)
            })
            
            return [init, for_loop, return_stmt]
            
        return node


def desugar_code(code: str, comment_density=0.3) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Transform Python code by expanding syntactic sugar.
    
    Args:
        code: Python source code string
        comment_density: Float between 0-1 controlling how many nodes get comments
        
    Returns:
        Tuple containing:
        - Transformed code
        - List of applied transformations
    """
    try:
        tree = ast.parse(code)
        
        original_comments = {}
        for i, line in enumerate(code.splitlines()):
            stripped = line.strip()
            if stripped.startswith('#'):
                original_comments[i] = line.strip()
        
        transformer = DesugarTransformer(comment_density, original_comments)
        transformed_tree = transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        
        transformed_code = astunparse.unparse(transformed_tree)
        
        final_lines = transformed_code.splitlines()
        inserted_comments = set()
        
        processed_lines = []
        
        for i, line in enumerate(final_lines):
            if i < len(final_lines) - 1 and not line.strip().startswith('#') and not final_lines[i+1].strip().startswith('#'):
                # Look for common code elements that should have comments
                if any(keyword in line for keyword in ['def ', 'class ', 'for ', 'if ', 'while ', 'with ']):
                    node_type = next((keyword.strip() for keyword in ['def ', 'class ', 'for ', 'if ', 'while ', 'with '] if keyword in line), None)
                    if node_type:
                        processed_lines.append(f"# This {node_type} statement performs a key operation in the code")
            
            processed_lines.append(line)
            
            # Add educational explanations after code constructs that have been expanded
            if line.strip() and not line.strip().startswith('#'):
                if 'result_list = []' in line or 'for ' in line and 'append' in line:
                    edu_comment = get_educational_explanation("list_comprehension")
                    processed_lines.append(edu_comment.strip())
                    inserted_comments.add("list_comprehension")
                    
                elif 'result_set = set()' in line or 'for ' in line and '.add(' in line:
                    edu_comment = get_educational_explanation("set_comprehension")
                    processed_lines.append(edu_comment.strip())
                    inserted_comments.add("set_comprehension")
                    
                elif 'result_dict = {}' in line or 'for ' in line and 'result_dict[' in line:
                    edu_comment = get_educational_explanation("dict_comprehension")
                    processed_lines.append(edu_comment.strip())
                    inserted_comments.add("dict_comprehension")
                    
                elif 'if ' in line and 'else' in line:
                    edu_comment = get_educational_explanation("ternary_operator")
                    processed_lines.append(edu_comment.strip())
                    inserted_comments.add("ternary_operator")
                    
                elif 'def generate' in line or 'yield ' in line:
                    edu_comment = get_educational_explanation("generator_expression")
                    processed_lines.append(edu_comment.strip())
                    inserted_comments.add("generator_expression")
                    
                elif 'enumerate(' in line:
                    edu_comment = get_educational_explanation("enumerate_pattern")
                    processed_lines.append(edu_comment.strip())
                    inserted_comments.add("enumerate_pattern")
        
        if not inserted_comments and not any(line.strip().startswith('#') for line in processed_lines):
            processed_lines.insert(0, "# This code has been expanded to a more verbose form with added explanations")
        
        desugared_code = "\n".join(processed_lines)
        
        return desugared_code, transformer.transformations
    except (SyntaxError, IndentationError, Exception) as e:
        return f"# Error desugarizing code: {str(e)}\n{code}", [] 