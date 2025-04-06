import unittest
import ast
import astunparse
import sys
import os

# Add parent directory to path to allow imports from project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from transformers.sugar_transformer import SugarTransformer, transform_code
from rules.sugaring_rules import SUGARING_RULEBOOK

class TestSugarTransformations(unittest.TestCase):
    
    def test_list_comprehension(self):
        """Test the list comprehension transformation."""
        # Input code with for loop and append
        input_code = """
result = []
for x in items:
    result.append(x * 2)
"""
        # Expected output with list comprehension
        expected_output = "result = [x * 2 for x in items]"
        
        # Transform the code
        transformed_code, transformations = transform_code(input_code)
        
        # Check that a transformation was applied
        self.assertTrue(len(transformations) > 0)
        self.assertEqual(transformations[0]['type'], 'list_comprehension')
        
        # Check that the transformed code contains a list comprehension
        self.assertIn('[x * 2 for x in items]', transformed_code.replace(' ', ''))
    
    def test_set_comprehension(self):
        """Test the set comprehension transformation."""
        # Input code with for loop and add
        input_code = """
result = set()
for x in items:
    result.add(x * 2)
"""
        # Transform the code
        transformed_code, transformations = transform_code(input_code)
        
        # Check that a transformation was applied
        self.assertTrue(len(transformations) > 0)
        self.assertEqual(transformations[0]['type'], 'set_comprehension')
        
        # Check that the transformed code contains a set comprehension
        self.assertIn('{x * 2 for x in items}', transformed_code.replace(' ', ''))
    
    def test_dict_comprehension(self):
        """Test the dictionary comprehension transformation."""
        # Input code with for loop and dict assignment
        input_code = """
result = {}
for x in items:
    result[x] = x * 2
"""
        # Transform the code
        transformed_code, transformations = transform_code(input_code)
        
        # Check that a transformation was applied
        self.assertTrue(len(transformations) > 0)
        self.assertEqual(transformations[0]['type'], 'dict_comprehension')
        
        # Check that the transformed code contains a dict comprehension
        self.assertIn('{x:x * 2 for x in items}', transformed_code.replace(' ', ''))
    
    def test_enumerate_transformation(self):
        """Test the enumerate transformation."""
        # Input code with manual counter
        input_code = """
i = 0
for item in items:
    print(i, item)
    i += 1
"""
        # Transform the code
        transformed_code, transformations = transform_code(input_code)
        
        # Check if the transformation was recognized
        # Note: Full transformation might not work without context across multiple statements
        for transform in transformations:
            if transform['type'] == 'enumerate_pattern':
                # Test passed if we identified the pattern
                self.assertIn('enumerate', transformed_code)
                return
        
        # If we reach here, no enumerate transformation was applied
        self.assertTrue(False, "Enumerate transformation not applied")
    
    def test_ternary_operator(self):
        """Test the ternary operator transformation."""
        # Input code with if/else for assignment
        input_code = """
if condition:
    result = value1
else:
    result = value2
"""
        # Transform the code
        transformed_code, transformations = transform_code(input_code)
        
        # Check if we have a ternary transformation
        for transform in transformations:
            if transform['type'] == 'ternary_operator':
                # Check the transformed code format
                self.assertIn('if condition else', transformed_code)
                return
                
        # If we reach here, no ternary transformation was applied
        self.assertTrue(False, "Ternary transformation not applied")
    
    def test_error_handling(self):
        """Test error handling with invalid code."""
        # Input code with syntax error
        input_code = """
def invalid_function():
    return x +
"""
        # Transform the code
        transformed_code, transformations = transform_code(input_code)
        
        # Check that we get an error message
        self.assertIn("# ERROR:", transformed_code)
        self.assertEqual(len(transformations), 0)

if __name__ == '__main__':
    unittest.main() 