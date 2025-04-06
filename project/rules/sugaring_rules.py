"""
Extended Rulebook for Python Syntactic Sugar Transformations.

Each rule defines:
- name: A unique identifier for the transformation.
- matches: A description of the verbose pattern.
- ast_pattern: A simplified representation of the AST nodes to match.
- sugar: The concise (sugared) construct.
- example: Code snippets showing the transformation ("before" and "after").
- explanation: A detailed explanation of why and when to use this sugar.
"""

SUGARING_RULEBOOK = [
    {
        "name": "list_comprehension",
        "matches": "for-loop with append",
        "ast_pattern": ["For", "Expr(value=Call(func=Attribute(attr='append'))...)"],
        "sugar": "ListComp",
        "example": {
            "before": """
result = []
for x in items:
    result.append(x * 2)
            """,
            "after": """
result = [x * 2 for x in items]
            """
        },
        "explanation": "List comprehensions allow you to create lists concisely by replacing a for-loop that appends values with a single, readable expression."
    },
    {
        "name": "set_comprehension",
        "matches": "for-loop with set.add",
        "ast_pattern": ["For", "Expr(value=Call(func=Attribute(attr='add'))...)"],
        "sugar": "SetComp",
        "example": {
            "before": """
result = set()
for x in items:
    result.add(x * 2)
            """,
            "after": """
result = {x * 2 for x in items}
            """
        },
        "explanation": "Set comprehensions replace loops that add elements to a set with a single concise expression."
    },
    {
        "name": "dict_comprehension",
        "matches": "for-loop with dict assignment",
        "ast_pattern": ["For", "Assign(targets=[Subscript(value=Name(id='result'))])"],
        "sugar": "DictComp",
        "example": {
            "before": """
result = {}
for x in items:
    result[x] = x * 2
            """,
            "after": """
result = {x: x * 2 for x in items}
            """
        },
        "explanation": "Dictionary comprehensions let you build dictionaries in one concise expression rather than a multi-line loop."
    },
    {
        "name": "enumerate_pattern",
        "matches": "manual counter with index access",
        "ast_pattern": [
            "Assign(targets=[Name(id='i')], value=Num(n=0))",
            "For",
            "AugAssign(target=Name(id='i'))"
        ],
        "sugar": "enumerate",
        "example": {
            "before": """
i = 0
for item in items:
    print(i, item)
    i += 1
            """,
            "after": """
for i, item in enumerate(items):
    print(i, item)
            """
        },
        "explanation": "The enumerate function returns both the index and the value when iterating over a sequence, eliminating the need for a manual counter."
    },
    {
        "name": "zip_pattern",
        "matches": "parallel iteration through index",
        "ast_pattern": ["For", "Subscript(value=Name(id='list1'))", "Subscript(value=Name(id='list2'))"],
        "sugar": "zip",
        "example": {
            "before": """
for i in range(len(list1)):
    item1 = list1[i]
    item2 = list2[i]
    print(item1, item2)
            """,
            "after": """
for item1, item2 in zip(list1, list2):
    print(item1, item2)
            """
        },
        "explanation": "The zip function allows simultaneous iteration over multiple sequences without explicit index manipulation."
    },
    {
        "name": "tuple_unpacking",
        "matches": "index-based tuple element access",
        "ast_pattern": [
            "Assign(targets=[Name(id='x')], value=Subscript(value=Name(id='tuple'), slice=Index(value=Num(n=0))))",
            "Assign(targets=[Name(id='y')], value=Subscript(value=Name(id='tuple'), slice=Index(value=Num(n=1))))"
        ],
        "sugar": "unpacking assignment",
        "example": {
            "before": """
tuple = (1, 2)
x = tuple[0]
y = tuple[1]
            """,
            "after": """
tuple = (1, 2)
x, y = tuple
            """
        },
        "explanation": "Tuple unpacking lets you assign multiple variables from a tuple in one concise statement."
    },
    {
        "name": "ternary_operator",
        "matches": "if-else for assignment",
        "ast_pattern": ["If", "Assign", "Else", "Assign"],
        "sugar": "ternary operator",
        "example": {
            "before": """
if condition:
    result = value1
else:
    result = value2
            """,
            "after": """
result = value1 if condition else value2
            """
        },
        "explanation": "The ternary operator condenses an if-else assignment into a single expression, improving readability."
    },
    {
        "name": "walrus_operator",
        "matches": "assign and use in condition",
        "ast_pattern": ["Assign", "If(test=Name)"],
        "sugar": "walrus operator",
        "example": {
            "before": """
match = pattern.search(string)
if match:
    result = match.group(1)
            """,
            "after": """
if match := pattern.search(string):
    result = match.group(1)
            """
        },
        "explanation": "The walrus operator (:=) lets you assign and test a variable in one expression, reducing repetition."
    },
    {
        "name": "with_statement",
        "matches": "try-finally with close",
        "ast_pattern": ["Try", "Finally", "Expr(value=Call(func=Attribute(attr='close')))"],
        "sugar": "with statement",
        "example": {
            "before": """
file = open('file.txt', 'r')
try:
    content = file.read()
finally:
    file.close()
            """,
            "after": """
with open('file.txt', 'r') as file:
    content = file.read()
            """
        },
        "explanation": "A with statement manages resources automatically, eliminating the need for explicit try-finally blocks."
    },
    {
        "name": "lambda_expression",
        "matches": "one-off simple function",
        "ast_pattern": ["FunctionDef", "Return"],
        "sugar": "lambda",
        "example": {
            "before": """
def double(x):
    return x * x
            """,
            "after": """
double = lambda x: x * x
            """
        },
        "explanation": "Lambda expressions let you define small anonymous functions inline, reducing boilerplate."
    },
    {
        "name": "generator_expression",
        "matches": "generator function with for-loop and yield",
        "ast_pattern": ["FunctionDef", "For", "Yield"],
        "sugar": "Generator Expression",
        "example": {
            "before": """
def gen():
    for x in items:
        yield x * 2
            """,
            "after": """
gen = (x * 2 for x in items)
            """
        },
        "explanation": "Generator expressions offer a concise syntax to create iterators without storing all items in memory."
    },
    {
        "name": "f_string_interpolation",
        "matches": "string concatenation with variables",
        "ast_pattern": ["BinOp", "Str"],
        "sugar": "f-string",
        "example": {
            "before": """
name = "Alice"
greeting = "Hello, " + name + "!"
            """,
            "after": """
name = "Alice"
greeting = f"Hello, {name}!"
            """
        },
        "explanation": "F-strings allow inline expression evaluation and produce cleaner, more readable string formatting."
    },
    {
        "name": "exception_suppression",
        "matches": "try-except pass for specific exception",
        "ast_pattern": ["Try", "ExceptHandler(pass)"],
        "sugar": "contextlib.suppress",
        "example": {
            "before": """
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass
            """,
            "after": """
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("temp.txt")
            """
        },
        "explanation": "Using contextlib.suppress streamlines exception handling by ignoring specified exceptions in a concise block."
    },
    {
        "name": "functools_partial",
        "matches": "wrapper function for fixed arguments",
        "ast_pattern": ["FunctionDef", "Lambda"],
        "sugar": "functools.partial",
        "example": {
            "before": """
def power(base, exponent):
    return base ** exponent
square = lambda x: power(x, 2)
            """,
            "after": """
from functools import partial
square = partial(pow, exp=2)
            """
        },
        "explanation": "functools.partial pre-fills function arguments, simplifying the creation of specialized functions."
    },
    {
        "name": "data_class",
        "matches": "class with explicit _init_ and _repr_",
        "ast_pattern": ["ClassDef", "FunctionDef(_init)", "FunctionDef(repr_)"],
        "sugar": "dataclass",
        "example": {
            "before": """
class Point:
    def _init_(self, x, y):
        self.x = x
        self.y = y
    def _repr_(self):
        return f"Point({self.x}, {self.y})"
            """,
            "after": """
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
            """
        },
        "explanation": "Data classes automatically generate common methods like _init_ and _repr_, reducing class boilerplate."
    },
    {
        "name": "decorator_syntax",
        "matches": "manual function wrapping assignment",
        "ast_pattern": ["FunctionDef", "Assign(wrapper)"],
        "sugar": "decorator",
        "example": {
            "before": """
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func._name_}")
        return func(*args, **kwargs)
    return wrapper

def add(a, b):
    return a + b
add = logger(add)
            """,
            "after": """
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func._name_}")
        return func(*args, **kwargs)
    return wrapper

@logger
def add(a, b):
    return a + b
            """
        },
        "explanation": "Using the @decorator syntax makes function wrapping more concise and readable than manual reassignment."
    },
    {
        "name": "yield_from",
        "matches": "nested loops yielding elements",
        "ast_pattern": ["FunctionDef", "For", "Yield"],
        "sugar": "yield from",
        "example": {
            "before": """
def chain(*iterables):
    for it in iterables:
        for element in it:
            yield element
            """,
            "after": """
def chain(*iterables):
    for it in iterables:
        yield from it
            """
        },
        "explanation": "The 'yield from' syntax delegates yielding to a subgenerator, simplifying generator code."
    },
    {
        "name": "extended_unpacking",
        "matches": "manual index-based unpacking of iterables",
        "ast_pattern": ["Assign", "Subscript", "Slice"],
        "sugar": "extended iterable unpacking",
        "example": {
            "before": """
a = numbers[0]
b = numbers[1]
rest = numbers[2:]
            """,
            "after": """
a, b, *rest = numbers
            """
        },
        "explanation": "Extended unpacking lets you capture multiple elements and the remainder of an iterable in one concise assignment."
    },
    {
        "name": "unpacking_operator_function_call",
        "matches": "manual argument extraction from a list",
        "ast_pattern": ["Call", "List"],
        "sugar": "argument unpacking with *",
        "example": {
            "before": """
args = [1, 2, 3]
result = func(args[0], args[1], args[2])
            """,
            "after": """
args = [1, 2, 3]
result = func(*args)
            """
        },
        "explanation": "Using the unpacking operator (*) in function calls simplifies passing arguments stored in sequences."
    },
    {
        "name": "dict_merging_unpacking",
        "matches": "manual dictionary merging via copy and update",
        "ast_pattern": ["Call(func=Attribute(attr='update'))"],
        "sugar": "dictionary merging with **",
        "example": {
            "before": """
new_dict = old_dict.copy()
new_dict.update(other_dict)
            """,
            "after": """
new_dict = {**old_dict, **other_dict}
            """
        },
        "explanation": "Merging dictionaries using the unpacking operator () creates a new dictionary in a single, concise expression."
    },
    {
        "name": "structural_pattern_matching",
        "matches": "multiple if/elif chains for type checking",
        "ast_pattern": ["If", "Compare", "Elif", "Else"],
        "sugar": "match/case",
        "example": {
            "before": """
if isinstance(value, int):
    process_int(value)
elif isinstance(value, str):
    process_str(value)
else:
    process_default(value)
            """,
            "after": """
match value:
    case int():
        process_int(value)
    case str():
        process_str(value)
    case _:
        process_default(value)
            """
        },
        "explanation": "Structural pattern matching provides a concise syntax for type or structure based branching."
    },
    {
        "name": "built_in_aggregators",
        "matches": "manual aggregation in a loop",
        "ast_pattern": ["For", "AugAssign"],
        "sugar": "sum()/min()/max()",
        "example": {
            "before": """
total = 0
for x in numbers:
    total += x
            """,
            "after": """
total = sum(numbers)
            """
        },
        "explanation": "Built-in functions like sum, min, or max condense common loops into a single function call."
    },
    {
        "name": "any_all_checks",
        "matches": "manual boolean check over iterable with loop and break",
        "ast_pattern": ["For", "If", "Break"],
        "sugar": "any()/all()",
        "example": {
            "before": """
found = False
for x in items:
    if condition(x):
        found = True
        break
            """,
            "after": """
found = any(condition(x) for x in items)
            """
        },
        "explanation": "Using any() or all() makes boolean checks over iterables more concise than a loop with manual flag-setting."
    },
    # --- Extra New Rules ---
    {
        "name": "reversed_iteration",
        "matches": "backwards loop with index arithmetic",
        "ast_pattern": ["For", "Call(func=Name(id='range'))", "Compare", "AugAssign"],
        "sugar": "reversed()",
        "example": {
            "before": """
for i in range(len(items)-1, -1, -1):
    print(items[i])
            """,
            "after": """
for item in reversed(items):
    print(item)
            """
        },
        "explanation": "The reversed() function simplifies iterating over a sequence in reverse order without manual index calculations."
    },
    {
        "name": "f_string_debug",
        "matches": "print with manual concatenation for debugging",
        "ast_pattern": ["Call", "Str", "BinOp"],
        "sugar": "f-string debug",
        "example": {
            "before": """
print("x =", x)
            """,
            "after": """
print(f"{x=}")
            """
        },
        "explanation": "F-string debugging prints variable names and values in a concise format, making debug output clearer."
    }
]