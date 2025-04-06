"""
Module for cleaning up redundant assignments in Python AST trees.
Removes unnecessary initializations before comprehension statements.
"""

import ast
from typing import Set, Dict, List

class RedundantAssignmentCleaner(ast.NodeTransformer):
    """
    Removes redundant container initializations before assignments to the same variable.
    
    Examples:
        result = []
        result = [x for x in items]
        
        Becomes:
        result = [x for x in items]
    """
    
    def visit_Module(self, node):
        """Process a module's top-level statements to find and remove redundant assignments."""
        var_assignments = {}
        
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                var_name = stmt.targets[0].id
                if var_name not in var_assignments:
                    var_assignments[var_name] = []
                var_assignments[var_name].append(i)
        
        to_remove = set()
        for var_name, indices in var_assignments.items():
            if len(indices) >= 2:
                for j in range(len(indices) - 1):
                    idx1, idx2 = indices[j], indices[j + 1]
                    
                    if idx2 - idx1 == 1:
                        assign1 = node.body[idx1]
                        assign2 = node.body[idx2]
                        
                        if (isinstance(assign1.value, ast.List) and len(assign1.value.elts) == 0 or
                            isinstance(assign1.value, ast.Dict) and len(assign1.value.keys) == 0 or
                            isinstance(assign1.value, ast.Call) and isinstance(assign1.value.func, ast.Name) and 
                            assign1.value.func.id == 'set' and len(assign1.value.args) == 0 or
                            isinstance(assign1.value, ast.Num) and assign1.value.n == 0):  
                            
                            to_remove.add(idx1)
        
        node.body = [stmt for i, stmt in enumerate(node.body) if i not in to_remove]
        
        self.generic_visit(node)
        return node 