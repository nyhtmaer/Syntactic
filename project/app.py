from flask import Flask, render_template, request, jsonify
import os
import ast
import astunparse
from transformers.sugar_transformer import transform_code
from transformers.desugar_transformer import desugar_code, DesugarTransformer
from rules.sugaring_rules import SUGARING_RULEBOOK
from utils.sugar_utils import (
    match_list_comprehension, match_set_comprehension, match_dict_comprehension,
    match_enumerate_pattern, match_ternary_operator, handle_code_errors,
    concise_comment
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/process_code', methods=['POST'])
def process_code():
    input_code = request.json.get('code', '')
    operation_type = request.json.get('operation', 'sugarize')  # Default to sugarize
    
    if operation_type == 'desugarize':
        return process_desugarize(input_code)
    else:
        return process_sugarize(input_code)

def process_sugarize(input_code):
    """Process code for sugarization (making code more concise)"""
    try:
        # Step 1: Parse the code and identify transformation candidates
        # Extract and preserve comments with their line numbers
        original_lines = input_code.splitlines()
        comments = {}
        
        for i, line in enumerate(original_lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                comments[i] = line
        
        parsed_ast = ast.parse(input_code)
        ast_dump = ast.dump(parsed_ast)
        
        # Step 2: Identify patterns for transformation
        potential_transformations = []
        
        # Simple pattern matching based on string representation
        # Using both AST string patterns for backward compatibility and our utility functions for better accuracy
        
        # List comprehension
        if "For(" in ast_dump and "Attribute(attr='append'" in ast_dump:
            potential_transformations.append({"type": "list_comprehension", "rule_ref": "list_comprehension"})

        # Set comprehension
        if "For(" in ast_dump and "Attribute(attr='add'" in ast_dump:
            potential_transformations.append({"type": "set_comprehension", "rule_ref": "set_comprehension"})

        # Dict comprehension
        if "For(" in ast_dump and "Subscript(value=Name" in ast_dump and "Assign(" in ast_dump:
            potential_transformations.append({"type": "dict_comprehension", "rule_ref": "dict_comprehension"})

        # Enumerate
        if "AugAssign(target=Name" in ast_dump and "For(" in ast_dump and "Add()" in ast_dump:
            potential_transformations.append({"type": "enumerate", "rule_ref": "enumerate_pattern"})

        # Ternary operator
        if "If(" in ast_dump and "Assign(" in ast_dump and "orelse=[" in ast_dump:
            potential_transformations.append({"type": "ternary_operator", "rule_ref": "ternary_operator"})

        # Remaining patterns kept the same for compatibility
        if "For(" in ast_dump and "Subscript(value=Name" in ast_dump and "range(len(" in input_code:
            potential_transformations.append({"type": "zip", "rule_ref": "zip_pattern"})

        if "Assign(" in ast_dump and "Subscript(value=Name" in ast_dump and "slice=Index(value=Num" in ast_dump:
            potential_transformations.append({"type": "tuple_unpacking", "rule_ref": "tuple_unpacking"})

        if "Try(" in ast_dump and "Finally(" in ast_dump and "Attribute(attr='close'" in ast_dump:
            potential_transformations.append({"type": "with_statement", "rule_ref": "with_statement"})

        if "If(" in ast_dump and "Call(func=Name(id='len', ctx=Load()))" in ast_dump and "Compare(left=Name" in ast_dump and "Eq()" in ast_dump:
            potential_transformations.append({"type": "any_all", "rule_ref": "any_all_pattern"})

        if "For(" in ast_dump and "Attribute(attr='pop'" in ast_dump and "Compare(left=Subscript(value=Name" in ast_dump and "NotEq()" in ast_dump:
            potential_transformations.append({"type": "list_filter", "rule_ref": "list_filter_pattern"})

        if "For(" in ast_dump and "Name(id='range', ctx=Load())" in ast_dump and "Subscript(value=Name" in ast_dump:
            potential_transformations.append({"type": "range_enumerate", "rule_ref": "range_enumerate_pattern"})

        if "If(" in ast_dump and "Compare(left=Name" in ast_dump and "Is()" in ast_dump:
            potential_transformations.append({"type": "identity_check", "rule_ref": "identity_check_pattern"})

        if "For(" in ast_dump and "Compare(left=Name" in ast_dump and "Gt()" in ast_dump:
            potential_transformations.append({"type": "range_filter", "rule_ref": "range_filter_pattern"})

        if "For(" in ast_dump and "Call(func=Name(id='set', ctx=Load()))" in ast_dump and "Attribute(attr='add'" in ast_dump:
            potential_transformations.append({"type": "set_add", "rule_ref": "set_add_pattern"})

        if "For(" in ast_dump and "Subscript(value=Name" in ast_dump and "Compare(left=Name" in ast_dump and "Eq()" in ast_dump:
            potential_transformations.append({"type": "dict_filter", "rule_ref": "dict_filter_pattern"})

        if "While(" in ast_dump and "Compare(left=Name" in ast_dump and "Lt()" in ast_dump:
            potential_transformations.append({"type": "while_loop", "rule_ref": "while_loop_pattern"})

        if "With(" in ast_dump and "Attribute(attr='open'" in ast_dump:
            potential_transformations.append({"type": "file_with", "rule_ref": "file_with_pattern"})

        if "FunctionDef(name='lambda')" in ast_dump and "arguments" in ast_dump:
            potential_transformations.append({"type": "lambda_function", "rule_ref": "lambda_function_pattern"})

        if "For(" in ast_dump and "Call(func=Name(id='map', ctx=Load()))" in ast_dump:
            potential_transformations.append({"type": "map_function", "rule_ref": "map_function_pattern"})

        if "If(" in ast_dump and "Attribute(attr='startswith'" in ast_dump and "Call(func=Name(id='str', ctx=Load()))" in ast_dump:
            potential_transformations.append({"type": "string_method_check", "rule_ref": "string_method_check_pattern"})

        if "Assign(" in ast_dump and "Call(func=Name(id='sorted', ctx=Load()))" in ast_dump:
            potential_transformations.append({"type": "sorted_assignment", "rule_ref": "sorted_assignment_pattern"})

        if "Call(func=Name(id='filter', ctx=Load()))" in ast_dump and "Compare(left=Name" in ast_dump and "Gt()" in ast_dump:
            potential_transformations.append({"type": "filter_range", "rule_ref": "filter_range_pattern"})

        if "For(" in ast_dump and "Attribute(attr='remove'" in ast_dump and "Compare(left=Subscript(value=Name" in ast_dump:
            potential_transformations.append({"type": "list_remove", "rule_ref": "list_remove_pattern"})

        if "For(" in ast_dump and "Call(func=Name(id='sorted', ctx=Load()))" in ast_dump and "Subscript(value=Name" in ast_dump:
            potential_transformations.append({"type": "sorted_list_comprehension", "rule_ref": "sorted_list_comprehension"})

        if "For(" in ast_dump and "Compare(left=Name" in ast_dump and "Lt()" in ast_dump:
            potential_transformations.append({"type": "filter_less_than", "rule_ref": "filter_less_than_pattern"})

        if "If(" in ast_dump and "Name(id='str', ctx=Load())" in ast_dump and "Call(func=Name(id='isdigit', ctx=Load()))" in ast_dump:
            potential_transformations.append({"type": "isdigit_check", "rule_ref": "isdigit_check_pattern"})

        if "For(" in ast_dump and "Attribute(attr='update'" in ast_dump and "Subscript(value=Name" in ast_dump:
            potential_transformations.append({"type": "dict_update", "rule_ref": "dict_update_pattern"})

        if "For(" in ast_dump and "Call(func=Name(id='filter', ctx=Load()))" in ast_dump and "Compare(left=Name" in ast_dump and "Gt()" in ast_dump:
            potential_transformations.append({"type": "filter_greater_than", "rule_ref": "filter_greater_than_pattern"})

        # Step 3: Apply transformations
        transformed_code, applied_transformations = transform_code(input_code, SUGARING_RULEBOOK)
        
        if not applied_transformations:
            if comments:
                # Make sure to include the original comments in their correct positions
                transformed_lines = input_code.splitlines()
                transformed_code = "\n".join(transformed_lines)
            else:
                transformed_code = "# No transformations were identified in the code.\n" + input_code
            
        # Step 4: Generate explanations for transformations
        explanations = []
        for transform in potential_transformations:
            rule_ref = transform.get("rule_ref", "")
            
            # Look up explanation in rulebook
            explanation = "No detailed explanation available."
            for rule in SUGARING_RULEBOOK:
                if rule["name"] == rule_ref:
                    explanation = rule["explanation"]
                    
                    # Add examples from rulebook
                    if "example" in rule:
                        explanation += f"\n\nExample:\nBefore:\n{rule['example']['before']}\n\nAfter:\n{rule['example']['after']}"
                    break
            
            explanations.append({
                "transformation_type": transform["type"],
                "explanation": explanation
            })
            
        # Step 5: Validate the transformed code
        validation_result = {
            "is_valid": True,
            "errors": []
        }
        
        try:
            # Compile both versions to check syntax
            compile(input_code, '<string>', 'exec')
            
            # Clean up transformed code by removing comments for compilation
            # But preserve comments for display
            cleaned_transformed_code = "\n".join([
                line for line in transformed_code.split("\n")
                if not line.strip().startswith("#")
            ])
            
            if cleaned_transformed_code.strip():  # Only compile if there's code
                compile(cleaned_transformed_code, '<string>', 'exec')
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(str(e))
            
        return jsonify({
            'original_code': input_code,
            'sugared_code': transformed_code,
            'comments': comments,
            'explanations': explanations,
            'validation': validation_result
        })
        
    except Exception as e:
        error_result, _ = handle_code_errors(input_code, e)
        return jsonify({
            'status': 'error',
            'message': error_result
        }), 500

def process_desugarize(input_code):
    """Process code for desugarization (expanding code and adding comments)"""
    try:
        # Step 1: Parse the code and extract original comments
        parsed_ast = ast.parse(input_code)
        ast_dump = ast.dump(parsed_ast)
        
        original_comments = {}
        for i, line in enumerate(input_code.splitlines()):
            stripped = line.strip()
            if stripped.startswith('#'):
                original_comments[i] = line
        
        # Step 2: Check for concise code constructs
        potential_expansions = []
        
        # Check for list comprehensions
        if "ListComp(" in ast_dump:
            potential_expansions.append({"type": "list_comprehension_expansion", "description": "Expanding list comprehension to for loop with append"})
            
        # Check for set comprehensions
        if "SetComp(" in ast_dump:
            potential_expansions.append({"type": "set_comprehension_expansion", "description": "Expanding set comprehension to for loop with add"})
            
        # Check for dict comprehensions
        if "DictComp(" in ast_dump:
            potential_expansions.append({"type": "dict_comprehension_expansion", "description": "Expanding dictionary comprehension to for loop with assignment"})
            
        # Check for ternary operators
        if "IfExp(" in ast_dump:
            potential_expansions.append({"type": "ternary_operator_expansion", "description": "Expanding ternary operator to if-else statement"})
            
        # Check for generator expressions
        if "GeneratorExp(" in ast_dump:
            potential_expansions.append({"type": "generator_expression_expansion", "description": "Expanding generator expression to generator function"})
            
        # Check for enumerate usage
        if "Name(id='enumerate'" in ast_dump:
            potential_expansions.append({"type": "enumerate_expansion", "description": "Expanding enumerate to counter-based loop"})
            
        # Check for sum usage
        if "Name(id='sum'" in ast_dump:
            potential_expansions.append({"type": "sum_expansion", "description": "Expanding sum to accumulator loop"})

        # Step 3: Apply desugarization transformations with a comment density of 0.4 (40% of nodes get comments)
        # Pass the original comments to preserve and enhance them
        desugared_code, applied_transformations = desugar_code(input_code, comment_density=0.4)
        
        # If no transformations were applied, provide a placeholder with some basic comments
        if not applied_transformations:
            parsed_ast = ast.parse(input_code)
            transformer = DesugarTransformer(comment_density=0.5, input_comments=original_comments)
            transformed_tree = transformer.visit(parsed_ast)
            ast.fix_missing_locations(transformed_tree)
            desugared_code = astunparse.unparse(transformed_tree)
            
            if not desugared_code.strip():
                desugared_code = "# No expansions were made. Code is already in a verbose form.\n" + input_code
        
        # Step 4: Generate explanations for transformations
        explanations = []
        for expansion in potential_expansions:
            explanations.append({
                "transformation_type": expansion["type"],
                "explanation": expansion["description"]
            })
        
        # Step 5: Validate the desugared code
        validation_result = {
            "is_valid": True,
            "errors": []
        }
        
        try:
            # Compile both versions to check syntax
            compile(input_code, '<string>', 'exec')
            
            # Clean up desugared code by removing comments for compilation
            # But preserve comments for display
            cleaned_desugared_code = "\n".join([
                line for line in desugared_code.split("\n")
                if not line.strip().startswith("#")
            ])
            
            if cleaned_desugared_code.strip():  # Only compile if there's code
                compile(cleaned_desugared_code, '<string>', 'exec')
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(str(e))
        
        return jsonify({
            'original_code': input_code,
            'desugared_code': desugared_code,
            'explanations': explanations,
            'validation': validation_result
        })
    
    except Exception as e:
        error_result, _ = handle_code_errors(input_code, e)
        return jsonify({
            'status': 'error',
            'message': error_result
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 