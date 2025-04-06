import ast
import json
from crewai import Agent
from rules.sugaring_rules import SUGARING_RULEBOOK
from utils.sugar_utils import (
    match_list_comprehension, match_set_comprehension, 
    match_dict_comprehension, match_enumerate_pattern, match_ternary_operator,
    match_generator_expression
)

class ParserAgent:
    """Agent that parses Python code into AST and identifies verbose constructs."""
    
    def __init__(self):
        self.name = "Parser Agent"
        self.description = "Analyzes Python code to find verbose constructs that can be rewritten with syntactic sugar."
        self.rules = SUGARING_RULEBOOK
    
    def get_agent(self):
        """Returns the CrewAI agent for this parser."""
        return Agent(
            role="Python Code Parser",
            goal="Parse Python code and identify verbose constructs that can be sugared",
            backstory="I'm an expert Python AST parser who can identify code patterns that can be simplified.",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.parse_code,
                self.identify_verbose_constructs
            ]
        )
    
    def parse_code(self, code):
        """Parse Python code string into an AST while preserving comments."""
        try:
            # Extracting and preserving comments with their line numbers.
            original_lines = code.splitlines()
            comments = {}
            
            for i, line in enumerate(original_lines):
                stripped = line.strip()
                if stripped.startswith('#'):
                    comments[i] = line
            
            # Parsing the code into AST.
            parsed_ast = ast.parse(code)
            
            return {
                "status": "success", 
                "ast": ast.dump(parsed_ast),
                "original_code": code,
                "comments": comments
            }
        except SyntaxError as e:
            return {"status": "error", "message": str(e)}
    
    def identify_verbose_constructs(self, ast_dump):
        """
        Analyzing the AST and identifing verbose constructs that can be sugared.
        Returns the AST with nodes tagged for potential transformation.
        """
        tagged_nodes = []
        
        # Converting the ast_dump string back to a Python object.
        # For this ,we will use pattern matching on the string representation.

        # List Comprehension: for-loop with append
        if "For(" in ast_dump and "Attribute(attr='append'" in ast_dump:
            tagged_nodes.append({
                "type": "list_comprehension",
                "rule_ref": "list_comprehension",
                "location": "location info would be here"
            })

        # Set Comprehension: for-loop with set.add
        if "For(" in ast_dump and "Attribute(attr='add'" in ast_dump:
            tagged_nodes.append({
                "type": "set_comprehension",
                "rule_ref": "set_comprehension",
                "location": "location info would be here"
            })

        # Dict Comprehension: for-loop with dict assignment
        if "For(" in ast_dump and "Assign(targets=[Subscript(value=Name(id='result'))])" in ast_dump:
            tagged_nodes.append({
                "type": "dict_comprehension",
                "rule_ref": "dict_comprehension",
                "location": "location info would be here"
            })

        # Enumerate Pattern: manual counter with index access
        if "Assign(targets=[Name(id='i')], value=Num(n=0))" in ast_dump and "AugAssign(target=Name(id='i'))" in ast_dump:
            tagged_nodes.append({
                "type": "enumerate_pattern",
                "rule_ref": "enumerate_pattern",
                "location": "location info would be here"
            })

        # Zip Pattern: parallel iteration through index
        if "For" in ast_dump and "Subscript(value=Name(id='list1'))" in ast_dump and "Subscript(value=Name(id='list2'))" in ast_dump:
            tagged_nodes.append({
                "type": "zip_pattern",
                "rule_ref": "zip_pattern",
                "location": "location info would be here"
            })

        # Tuple Unpacking: index-based tuple element access
        if "Assign(targets=[Name(id='x')], value=Subscript(value=Name(id='tuple'), slice=Index(value=Num(n=0))))" in ast_dump and "Assign(targets=[Name(id='y')], value=Subscript(value=Name(id='tuple'), slice=Index(value=Num(n=1))))" in ast_dump:
            tagged_nodes.append({
                "type": "tuple_unpacking",
                "rule_ref": "tuple_unpacking",
                "location": "location info would be here"
            })

        # Ternary Operator: if-else for assignment
        if "If" in ast_dump and "Assign" in ast_dump and "Else" in ast_dump:
            tagged_nodes.append({
                "type": "ternary_operator",
                "rule_ref": "ternary_operator",
                "location": "location info would be here"
            })

        # Walrus Operator: assign and use in condition
        if "Assign" in ast_dump and "If(test=Name)" in ast_dump:
            tagged_nodes.append({
                "type": "walrus_operator",
                "rule_ref": "walrus_operator",
                "location": "location info would be here"
            })

        # With Statement: try-finally with close
        if "Try" in ast_dump and "Finally" in ast_dump and "Expr(value=Call(func=Attribute(attr='close')))":
            tagged_nodes.append({
                "type": "with_statement",
                "rule_ref": "with_statement",
                "location": "location info would be here"
            })

        # Lambda Expression: one-off simple function
        if "FunctionDef" in ast_dump and "Return" in ast_dump:
            tagged_nodes.append({
                "type": "lambda_expression",
                "rule_ref": "lambda_expression",
                "location": "location info would be here"
            })

        # Generator Expression: generator function with for-loop and yield
        if "FunctionDef" in ast_dump and "For" in ast_dump and "Yield" in ast_dump:
            tagged_nodes.append({
                "type": "generator_expression",
                "rule_ref": "generator_expression",
                "location": "location info would be here"
            })

        # F-String Interpolation: string concatenation with variables
        if "BinOp" in ast_dump and "Str" in ast_dump:
            tagged_nodes.append({
                "type": "f_string_interpolation",
                "rule_ref": "f_string_interpolation",
                "location": "location info would be here"
            })

        # Exception Suppression: try-except pass for specific exception
        if "Try" in ast_dump and "ExceptHandler(pass)" in ast_dump:
            tagged_nodes.append({
                "type": "exception_suppression",
                "rule_ref": "exception_suppression",
                "location": "location info would be here"
            })

        # functools.partial: wrapper function for fixed arguments
        if "FunctionDef" in ast_dump and "Lambda" in ast_dump:
            tagged_nodes.append({
                "type": "functools_partial",
                "rule_ref": "functools_partial",
                "location": "location info would be here"
            })

        # Data Class: class with explicit _init_ and _repr_
        if "ClassDef" in ast_dump and "FunctionDef(_init)" in ast_dump and "FunctionDef(repr_)" in ast_dump:
            tagged_nodes.append({
                "type": "data_class",
                "rule_ref": "data_class",
                "location": "location info would be here"
            })

        # Decorator Syntax: manual function wrapping assignment
        if "FunctionDef" in ast_dump and "Assign(wrapper)" in ast_dump:
            tagged_nodes.append({
                "type": "decorator_syntax",
                "rule_ref": "decorator_syntax",
                "location": "location info would be here"
            })

        # Yield From: nested loops yielding elements
        if "FunctionDef" in ast_dump and "For" in ast_dump and "Yield" in ast_dump:
            tagged_nodes.append({
                "type": "yield_from",
                "rule_ref": "yield_from",
                "location": "location info would be here"
            })

        # Extended Unpacking: manual index-based unpacking of iterables
        if "Assign" in ast_dump and "Subscript" in ast_dump and "Slice" in ast_dump:
            tagged_nodes.append({
                "type": "extended_unpacking",
                "rule_ref": "extended_unpacking",
                "location": "location info would be here"
            })

        # Unpacking Operator Function Call: manual argument extraction from a list
        if "Call" in ast_dump and "List" in ast_dump:
            tagged_nodes.append({
                "type": "unpacking_operator_function_call",
                "rule_ref": "unpacking_operator_function_call",
                "location": "location info would be here"
            })
        
        return {
            "status": "success",
            "ast": ast_dump,
            "tagged_nodes": tagged_nodes
        }

        
    def process(self, code):
        """Main entry point for the parser agent."""
        parse_result = self.parse_code(code)
        
        if parse_result["status"] == "error":
            return parse_result
        
        identification_result = self.identify_verbose_constructs(parse_result["ast"])
        
        combined_result = {
            "status": identification_result["status"],
            "ast": identification_result["ast"],
            "tagged_nodes": identification_result["tagged_nodes"],
            "original_code": parse_result.get("original_code", ""),
            "comments": parse_result.get("comments", {})
        }
        
        return combined_result 