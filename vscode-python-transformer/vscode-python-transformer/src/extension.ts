import * as vscode from 'vscode';
import axios from 'axios';
import * as cp from 'child_process';
import * as path from 'path';

// Set up the transformation service URL - replace with your service URL or localhost
const SERVICE_URL = 'http://localhost:5000/process_code';
let pythonProcess: cp.ChildProcess | null = null;

export function activate(context: vscode.ExtensionContext) {
    // Register the sugarize command
    let sugarizeCommand = vscode.commands.registerCommand('python-transformer.sugarize', () => {
        transformCode('sugarize');
    });

    // Register the desugarize command
    let desugarizeCommand = vscode.commands.registerCommand('python-transformer.desugarize', () => {
        transformCode('desugarize');
    });
    
    // Register command to start the Python server
    let startServerCommand = vscode.commands.registerCommand('python-transformer.startServer', () => {
        startPythonServer(context.extensionPath);
    });
    
    // Register command to stop the Python server
    let stopServerCommand = vscode.commands.registerCommand('python-transformer.stopServer', () => {
        stopPythonServer();
    });

    // Add commands to the extension context
    context.subscriptions.push(
        sugarizeCommand, 
        desugarizeCommand,
        startServerCommand,
        stopServerCommand
    );
    
    // Auto-start the Python server when the extension activates
    startPythonServer(context.extensionPath);
}

interface TransformationResponse {
    status?: string;
    message?: string;
    sugared_code?: string;
    desugared_code?: string;
    expanded_code?: string;
}

// Function to transform code based on the operation type
async function transformCode(operation: string) {
    // Get active text editor
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found!');
        return;
    }

    // Verify it's a Python file
    if (editor.document.languageId !== 'python') {
        vscode.window.showErrorMessage('This command is only available for Python files!');
        return;
    }

    // Get the selected text or all text if nothing is selected
    const selection = editor.selection;
    const text = selection.isEmpty
        ? editor.document.getText()
        : editor.document.getText(selection);

    // No text to transform
    if (!text) {
        vscode.window.showErrorMessage('No code to transform!');
        return;
    }

    // If the server is not running, try to start it
    if (!pythonProcess) {
        // Ask the user to start the server
        const startServer = await vscode.window.showInformationMessage(
            'The Python transformation server is not running. Would you like to start it now?',
            'Yes', 'No'
        );
        
        if (startServer === 'Yes') {
            const extensionPath = vscode.extensions.all.find(
                ext => ext.packageJSON.name === 'vscode-python-transformer'
            )?.extensionPath;
            
            if (extensionPath) {
                startPythonServer(extensionPath);
            } else {
                vscode.window.showErrorMessage('Could not determine extension path.');
                return;
            }
        }
        
    }

    // Show progress indicator
    vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `${operation === 'sugarize' ? 'Making code concise' : 'Expanding code'}...`,
        cancellable: false
    }, async (progress: vscode.Progress<{ message?: string; increment?: number }>) => {
        try {
            // Call the API
            const response = await callTransformationAPI(text, operation);
            
            if (response.status === 'error') {
                vscode.window.showErrorMessage(`Error: ${response.message}`);
                return;
            }
            
            // Get the transformed code from the response
            const transformedCode = operation === 'sugarize' 
                ? response.sugared_code 
                : response.desugared_code || response.expanded_code;
            
            // Replace the selected text or all text with the transformed code
            editor.edit((editBuilder: vscode.TextEditorEdit) => {
                if (selection.isEmpty) {
                    // Replace the entire document
                    const fullRange = new vscode.Range(
                        0, 0,
                        editor.document.lineCount - 1,
                        editor.document.lineAt(editor.document.lineCount - 1).text.length
                    );
                    editBuilder.replace(fullRange, transformedCode || '');
                } else {
                    // Replace only the selected text
                    editBuilder.replace(selection, transformedCode || '');
                }
            });
            
            // Show success message
            vscode.window.showInformationMessage(
                `Code ${operation === 'sugarize' ? 'made concise' : 'expanded'} successfully!`
            );
            
        } catch (error) {
            vscode.window.showErrorMessage(
                `Failed to ${operation} code. Please ensure the transformation service is running.`
            );
        }
    });
}

async function callTransformationAPI(code: string, operation: string): Promise<TransformationResponse> {
    try {
        // First, try the remote service
        const response = await axios.post(SERVICE_URL, {
            code: code,
            operation: operation
        });
        return response.data;
    } catch (error: any) {
        // If the remote service fails, inform the user they need to set up the local service
        if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
            vscode.window.showErrorMessage(
                'Could not connect to Python transformation service. Make sure the service is running locally.'
            );
            
            // Provide instructions for setting up the local service
            const openInstructions = 'View Setup Instructions';
            const result = await vscode.window.showInformationMessage(
                'To use this extension, you need to run the Python code transformation service locally.',
                openInstructions
            );
            
            if (result === openInstructions) {
                // Show instructions in a new untitled document
                const document = await vscode.workspace.openTextDocument({
                    content: getServiceSetupInstructions(),
                    language: 'markdown'
                });
                await vscode.window.showTextDocument(document);
            }
        }
        
        return { status: 'error', message: 'Failed to transform code. Service unavailable.' };
    }
}

function startPythonServer(extensionPath: string) {
    try {
        // If the server is already running, don't start a new one
        if (pythonProcess) {
            vscode.window.showInformationMessage('Python transformation server is already running.');
            return;
        }
        
        // Path to the Python server directory
        const serverPath = path.join(extensionPath, 'python-server');
        
        // Find the Python executable
        const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
        
        // Command to run the server
        const command = `${pythonCommand} ${path.join(serverPath, 'app.py')}`;
        
        // Start the Python process
        pythonProcess = cp.exec(command, { cwd: serverPath }, (error, stdout, stderr) => {
            if (error) {
                vscode.window.showErrorMessage(`Failed to start Python server: ${error.message}`);
                pythonProcess = null;
            }
        });
        
        // Listen for process exit
        if (pythonProcess) {
            pythonProcess.on('exit', (code) => {
                vscode.window.showInformationMessage(`Python server stopped with code ${code}`);
                pythonProcess = null;
            });
            
            vscode.window.showInformationMessage('Python transformation server started.');
        }
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to start Python server: ${error.message}`);
    }
}

function stopPythonServer() {
    if (pythonProcess) {
        // Kill the process
        if (process.platform === 'win32') {
            // On Windows, we need to use taskkill to kill the process and its children
            cp.exec(`taskkill /pid ${pythonProcess.pid} /f /t`);
        } else {
            // On Unix-like systems, we can kill the process directly
            pythonProcess.kill();
        }
        
        pythonProcess = null;
        vscode.window.showInformationMessage('Python transformation server stopped.');
    } else {
        vscode.window.showInformationMessage('Python transformation server is not running.');
    }
}

function getServiceSetupInstructions(): string {
    return `# Python Code Transformer Service Setup

To use the VS Code Python Code Transformer extension, you need to run the Python transformation service locally:

1. Start the service using the command:
   - Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
   - Type "Python: Start Transformation Server" and select it

2. If the service fails to start automatically, you can:
   - Navigate to the python-server directory in your extension folder
   - Run \`pip install -r requirements.txt\` to install dependencies
   - Run \`python app.py\` to start the server

3. The service should be running at http://localhost:5000

4. Once the service is running, you can use the extension to transform Python code.
`;
}

export function deactivate() {
    // Stop the Python server when the extension is deactivated
    stopPythonServer();
} 