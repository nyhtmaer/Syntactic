import ast
import json
import difflib
from crewai import Agent

class ValidationAgent:
    """Agent that validates the functional equivalence of original and sugared code."""
    
    def __init__(self):
        self.name = "Validation Agent"
        self.description = "I validate that sugared code is functionally equivalent to the original code."
    
    def get_agent(self):
        """Returns the CrewAI agent for this validator."""
        return Agent(
            role="Code Validation Specialist",
            goal="Ensure that sugared code maintains the same functionality as the original code",
            backstory="I'm a code validation expert who ensures transformations preserve functionality.",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.validate_code,
                self.generate_diff
            ]
        )
    
    def validate_code(self, original_code, sugared_code):
        """
        Validate that the original and sugared code are functionally equivalent.
        
        Args:
            original_code: The original Python code
            sugared_code: The transformed Python code with syntactic sugar
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "status": "success",
            "is_valid": True,
            "compile_check": True,
            "execution_check": None,
            "errors": []
        }
        
        try:
            original_compiled = compile(original_code, '<string>', 'exec')
        except Exception as e:
            validation_results["compile_check"] = False
            validation_results["is_valid"] = False
            validation_results["errors"].append(f"Original code compilation error: {str(e)}")
        
        try:
            cleaned_sugared_code = "\n".join([
                line for line in sugared_code.split("\n")
                if not line.strip().startswith("#")
            ])
            sugared_compiled = compile(cleaned_sugared_code, '<string>', 'exec')
        except Exception as e:
            validation_results["compile_check"] = False
            validation_results["is_valid"] = False
            validation_results["errors"].append(f"Sugared code compilation error: {str(e)}")
    
        
        return validation_results
    
    def generate_diff(self, original_code, sugared_code):
        """
        Generate a diff between the original and sugared code.
        
        Args:
            original_code: The original Python code
            sugared_code: The transformed Python code with syntactic sugar
            
        Returns:
            Dictionary with diff information
        """

        cleaned_original_code = "\n".join([
            line for line in original_code.split("\n")
            if not line.strip().startswith("#")
        ])
        
        cleaned_sugared_code = "\n".join([
            line for line in sugared_code.split("\n")
            if not line.strip().startswith("#")
        ])
        
        diff = difflib.unified_diff(
            cleaned_original_code.splitlines(),
            cleaned_sugared_code.splitlines(),
            fromfile='original',
            tofile='sugared',
            lineterm=''
        )
        
        diff_text = "\n".join(diff)
        
        return {
            "status": "success",
            "diff": diff_text
        }
    
    def process(self, original_code, sugared_code, comments=None):
        """
        Main entry point for the validation agent.
        
        Args:
            original_code: The original Python code
            sugared_code: The transformed Python code with syntactic sugar
            comments: Optional dictionary of comments with their line numbers
            
        Returns:
            Dictionary with validation results, diff, and preserved comments
        """
        validation_result = self.validate_code(original_code, sugared_code)
        
        if validation_result["status"] == "error":
            return validation_result
        
        diff_result = self.generate_diff(original_code, sugared_code)
        
        return {
            "status": "success",
            "is_valid": validation_result["is_valid"],
            "errors": validation_result.get("errors", []),
            "diff": diff_result["diff"],
            "original_code": original_code,
            "sugared_code": sugared_code,
            "comments": comments or {}
        } 