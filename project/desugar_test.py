"""
Test file for desugarizing Python code.
"""

from transformers.desugar_transformer import desugar_code

def test_desugar_list_comprehension():
    """Test expanding a list comprehension."""
    code = """
# Original concise code
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers if x % 2 == 0]
print(squares)
"""
    
    try:
        desugared_code, transformations = desugar_code(code)
        print("\n=== List Comprehension Desugarization ===")
        print("Original code:")
        print(code)
        print("Desugared code:")
        print(desugared_code)
        print("Transformations:", transformations)
    except Exception as e:
        print(f"Error in list comprehension test: {e}")

def test_desugar_ternary():
    """Test expanding a ternary operator."""
    code = """
# Original concise code
x = 10
result = "Even" if x % 2 == 0 else "Odd"
print(result)
"""
    
    try:
        desugared_code, transformations = desugar_code(code)
        print("\n=== Ternary Operator Desugarization ===")
        print("Original code:")
        print(code)
        print("Desugared code:")
        print(desugared_code)
        print("Transformations:", transformations)
    except Exception as e:
        print(f"Error in ternary operator test: {e}")

def test_desugar_generator():
    """Test expanding a generator expression."""
    code = """
# Original concise code
numbers = [1, 2, 3, 4, 5]
gen = (x**2 for x in numbers if x % 2 == 0)
for num in gen:
    print(num)
"""
    
    try:
        desugared_code, transformations = desugar_code(code)
        print("\n=== Generator Expression Desugarization ===")
        print("Original code:")
        print(code)
        print("Desugared code:")
        print(desugared_code)
        print("Transformations:", transformations)
    except Exception as e:
        print(f"Error in generator expression test: {e}")

if __name__ == "__main__":
    try:
        test_desugar_list_comprehension()
        test_desugar_ternary()
        test_desugar_generator()
    except Exception as e:
        print(f"Unexpected error running tests: {e}") 