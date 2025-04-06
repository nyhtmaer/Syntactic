// JavaScript for Python Code Transformation Tool

document.addEventListener('DOMContentLoaded', () => {
    // Initialize CodeMirror for original code
    const originalEditor = CodeMirror.fromTextArea(document.getElementById('original-code'), {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        indentUnit: 4,
        matchBrackets: true,
        autofocus: true
    });

    // Initialize CodeMirror for transformed code
    const transformedEditor = CodeMirror.fromTextArea(document.getElementById('transformed-code'), {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        indentUnit: 4,
        matchBrackets: true,
        readOnly: true
    });

    // Get DOM elements
    const processBtn = document.getElementById('process-btn');
    const explanationsContent = document.getElementById('explanations-content');
    const diffContent = document.getElementById('diff-content');
    const validationStatus = document.getElementById('validation-status');
    const loadingOverlay = document.getElementById('loading');
    const explanationsPanel = document.getElementById('explanations-panel');
    const diffPanel = document.getElementById('diff-panel');
    const resultTitle = document.getElementById('result-title');
    const operationRadios = document.querySelectorAll('input[name="operation"]');

    // Hide panels initially
    explanationsPanel.style.display = 'none';
    diffPanel.style.display = 'none';

    // Update result title based on operation selection
    operationRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            updateResultTitle(radio.value);
        });
    });

    function updateResultTitle(operation) {
        if (operation === 'sugarize') {
            resultTitle.textContent = 'Sugared Code';
        } else {
            resultTitle.textContent = 'Expanded Code';
        }
    }

    // Set initial title
    updateResultTitle('sugarize');

    // Process button click handler
    processBtn.addEventListener('click', async () => {
        const originalCode = originalEditor.getValue();
        
        // Get the selected operation
        const selectedOperation = document.querySelector('input[name="operation"]:checked').value;
        
        // Check if there's any code to process
        if (!originalCode.trim()) {
            validationStatus.innerHTML = `
                <div class="validation-error">
                    <p>Please enter some Python code first.</p>
                </div>
            `;
            return;
        }
        
        // Show loading overlay
        loadingOverlay.style.display = 'flex';
        
        // Call the backend API to process the code
        try {
            const response = await fetch('/process_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    code: originalCode,
                    operation: selectedOperation
                })
            });
            
            if (!response.ok) {
                console.error('Server error:', response.statusText);
                
                // Show a user-friendly message instead of a pop-up alert
                validationStatus.innerHTML = `
                    <div class="validation-error">
                        <p>There was an issue processing the code. Please try again later.</p>
                    </div>
                `;
                return;  // Prevent further processing
            }
            
            const result = await response.json();
            
            // Update transformed code based on the operation
            if (selectedOperation === 'sugarize') {
                transformedEditor.setValue(result.sugared_code);
            } else {
                transformedEditor.setValue(result.desugared_code);
            }
            
            // Update validation status
            updateValidationStatus(result.validation);
            
            // Update explanations
            updateExplanations(result.explanations);
            
            // Update diff view
            updateDiffView(
                result.original_code, 
                selectedOperation === 'sugarize' ? result.sugared_code : result.desugared_code,
                selectedOperation
            );
            
            // Show panels
            explanationsPanel.style.display = 'block';
            diffPanel.style.display = 'block';
            
        } catch (error) {
            console.error('Error:', error);
    
            // Check if the error is related to Diff2Html not being loaded
            if (error.message.includes('Diff2Html is not defined')) {
                // Gracefully handle the case where Diff2Html is missing
                console.error('Diff2Html library is not loaded. Diff rendering will be skipped.');
                validationStatus.innerHTML = `
                    <div class="validation-warning">
                        <p></p>
                    </div>
                `;
            } else {
                // For other errors, display the error in the validation area
                validationStatus.innerHTML = `
                    <div class="validation-error">
                        <p>An error occurred: ${error.message}</p>
                    </div>
                `;
            }
        } finally {
            // Hide loading overlay
            loadingOverlay.style.display = 'none';
        }
    });
    
    // Function to update validation status
    function updateValidationStatus(validation) {
        validationStatus.innerHTML = '';
        
        if (validation.is_valid) {
            validationStatus.innerHTML = `
                <div class="validation-success">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                    </svg>
                    Validated: Code transformation is functionally equivalent
                </div>
            `;
        } else {
            const errorsList = validation.errors.map(err => `<li>${err}</li>`).join('');
            validationStatus.innerHTML = `
                <div class="validation-error">
                    <p>Validation failed:</p>
                    <ul>${errorsList}</ul>
                </div>
            `;
        }
    }

    // Function to update explanations
    function updateExplanations(explanations) {
        explanationsContent.innerHTML = '';
        
        if (explanations.length === 0) {
            explanationsContent.innerHTML = '<p>No transformations applied.</p>';
            return;
        }
        
        explanations.forEach(explanation => {
            const item = document.createElement('div');
            item.className = 'explanation-item';
            
            item.innerHTML = `
                <div class="transformation-type">${titleCase(explanation.transformation_type.replace(/_/g, ' '))}</div>
                <p>${explanation.explanation}</p>
            `;
            
            explanationsContent.appendChild(item);
        });
    }

    // Function to update diff view
    function updateDiffView(originalCode, transformedCode, operation) {
        // Clean up the transformed code by removing comments for diff
        const cleanedTransformedCode = transformedCode.split('\n')
            .filter(line => !line.trim().startsWith('#'))
            .join('\n');
        
        // Create a unified diff
        const diffString = createUnifiedDiff(originalCode, cleanedTransformedCode);
        
        // Render with diff2html
        const diffHtml = Diff2Html.html(diffString, {
            drawFileList: false,
            matching: 'lines',
            outputFormat: 'side-by-side'
        });
        
        diffContent.innerHTML = diffHtml;
    }

    // Helper function to create a unified diff
    function createUnifiedDiff(originalText, newText) {
        const originalLines = originalText.split('\n');
        const newLines = newText.split('\n');
        
        // Create a simple unified diff format
        let diffOutput = '--- original\n+++ transformed\n';
        let lineNumber = 1;
        
        for (let i = 0; i < Math.max(originalLines.length, newLines.length); i++) {
            const originalLine = originalLines[i] || '';
            const newLine = newLines[i] || '';
            
            if (originalLine !== newLine) {
                diffOutput += `@@ -${lineNumber},1 +${lineNumber},1 @@\n`;
                diffOutput += `-${originalLine}\n`;
                diffOutput += `+${newLine}\n`;
            }
            
            lineNumber++;
        }
        
        return diffOutput;
    }

    // Helper function to convert string to title case
    function titleCase(str) {
        return str.replace(
            /\w\S*/g,
            function(txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            }
        );
    }

    // Example code for demonstration
    const exampleCode = `# Example: List comprehension
result = []
for x in items:
    result.append(x * 2)

# Example: Manual counter with enumerate
i = 0
for item in items:
    print(i, item)
    i += 1`;
    
    // Set example code
    originalEditor.setValue(exampleCode);
}); 