import ast
import json
import astunparse
from crewai import Agent
from rules.sugaring_rules import SUGARING_RULEBOOK
import anthropic
import keys

class SugaringAgent:
    """Agent that transforms verbose code into sugared versions with explanations."""
    
    def __init__(self):
        self.name = "Sugaring Agent"
        self.description = "I transform verbose Python code into more concise versions using syntactic sugar."
        self.rules = SUGARING_RULEBOOK
        
        # Initializing the Claude client
        try:
            self.claude_client = anthropic.Anthropic(
                api_key= keys.api_key # Your own ID.
            )
        except:
            self.claude_client = None
    
    def get_agent(self):
        """Returns the CrewAI agent for this sugaring transformer."""
        return Agent(
            role="Python Code Transformer",
            goal="Transform verbose Python code into concise, sugared versions",
            backstory="I'm an expert at Python syntax who specializes in making code more elegant and readable.",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.transform_code,
                self.generate_explanation
            ]
        )
    
    def transform_code(self, parser_output):
        
        # Fetching AST and tagged nodes from parser output
        ast_dump = parser_output.get("ast", "")
        tagged_nodes = parser_output.get("tagged_nodes", [])
        original_code = parser_output.get("original_code", "")
        comments = parser_output.get("comments", {})
        
        # Starting with dummy transformations for the MVP
        sugared_code = "# Transformed code would be here\n"
        
        if tagged_nodes:
            for node in tagged_nodes:
                if node["type"] == "list_comprehension":
                    sugared_code += "# Example: Transformed a for-loop with append into list comprehension\n"
                    sugared_code += "result = [x * 2 for x in items]\n"

                elif node["type"] == "enumerate":
                    sugared_code += "# Example: Transformed a manual counter loop into enumerate\n"
                    sugared_code += "for i, item in enumerate(items):\n    print(i, item)\n"

                elif node["type"] == "set_comprehension":
                    sugared_code += "# Example: Transformed a for-loop into set comprehension\n"
                    sugared_code += "result = {x * 2 for x in items}\n"

                elif node["type"] == "dict_comprehension":
                    sugared_code += "# Example: Transformed a for-loop into dictionary comprehension\n"
                    sugared_code += "result = {x: x * 2 for x in items}\n"

                elif node["type"] == "for_loop_with_append":
                    sugared_code += "# Example: Transformed a for-loop with append into list comprehension\n"
                    sugared_code += "result = [x * 2 for x in items]\n"

                elif node["type"] == "zip":
                    sugared_code += "# Example: Transformed two loops into zip()\n"
                    sugared_code += "for a, b in zip(list_a, list_b):\n    print(a, b)\n"
                
                elif node["type"] == "tuple_unpacking":
                    sugared_code += "# Example: Transformed tuple unpacking in a for-loop\n"
                    sugared_code += "for (a, b) in items:\n    print(a, b)\n"

                elif node["type"] == "filter_map":
                    sugared_code += "# Example: Transformed for-loop with filter() or map()\n"
                    sugared_code += "filtered_items = filter(lambda x: x > 10, items)\n"
                    sugared_code += "mapped_items = map(lambda x: x * 2, items)\n"
                
                elif node["type"] == "if_statements":
                    sugared_code += "# Example: Simplified multiple if statements with any() or all()\n"
                    sugared_code += "if any(x > 10 for x in items):\n    print('Some items are greater than 10')\n"
                    sugared_code += "if all(x > 10 for x in items):\n    print('All items are greater than 10')\n"
            
            # If none of the transformations were identified
            if not tagged_nodes:
                sugared_code = "# No transformations were identified in the code."
        
        return {
            "status": "success",
            "original_ast": ast_dump,
            "original_code": original_code,
            "comments": comments,
            "code": sugared_code,
            "transformations": tagged_nodes
        }

    
    def generate_explanation(self, transformation_result):
        explanations = []
        transformations = transformation_result.get("transformations", [])
        
        for transform in transformations:
            rule_ref = transform.get("rule_ref", "")
            
            explanation = "No detailed explanation available."
            
            for rule in self.rules:
                if rule["name"] == rule_ref:
                    explanation = rule["explanation"]
                    break
            
            # Use Claude (if available) to enhance the explanation
            if self.claude_client:
                try:
                    message = self.claude_client.messages.create(
                        model="claude-3-7-sonnet-20240307",
                        max_tokens=300,
                        messages=[
                            {
                                "role": "user", 
                                "content": f"Explain why this Python transformation improves code quality: {rule_ref}. Keep your response under 100 words."
                            }
                        ]
                    )
                    claude_explanation = message.content
                    explanation = claude_explanation
                except Exception as e:
                    pass
            
            explanations.append({
                "transformation_type": transform["type"],
                "explanation": explanation
            })
        
        return {
            "status": "success",
            "explanations": explanations
        }
    
    def process(self, parser_output):
        """Main entry point for the sugaring agent."""
        transform_result = self.transform_code(parser_output)
        
        if transform_result["status"] == "error":
            return transform_result
        
        explanation_result = self.generate_explanation(transform_result)
        
        # Combining results including original code and comments
        return {
            "status": "success",
            "code": transform_result["code"],
            "original_code": transform_result.get("original_code", ""),
            "comments": transform_result.get("comments", {}),
            "explanations": explanation_result["explanations"]
        } 