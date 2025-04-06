// Simple script to copy the Python backend files to the extension's 'python-server' directory
// This can be used during development and packaging to include the Python backend with the extension

const fs = require('fs');
const path = require('path');

// Source and destination directories
const sourceDir = '../project - Copy';
const destDir = './python-server';

// Create the destination directory if it doesn't exist
if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
}

// Function to copy directories recursively
function copyDir(src, dest) {
    // Create destination directory if it doesn't exist
    if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
    }
    
    // Get all files and directories in the source directory
    const entries = fs.readdirSync(src, { withFileTypes: true });
    
    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        
        // Skip __pycache__ directories and .pyc files
        if (entry.name === '__pycache__' || entry.name.endsWith('.pyc')) {
            continue;
        }
        
        // Recursively copy directories
        if (entry.isDirectory()) {
            copyDir(srcPath, destPath);
        } else {
            // Copy files
            fs.copyFileSync(srcPath, destPath);
            console.log(`Copied: ${srcPath} -> ${destPath}`);
        }
    }
}

// Copy necessary Python files
try {
    // Copy app.py
    fs.copyFileSync(path.join(sourceDir, 'app.py'), path.join(destDir, 'app.py'));
    console.log(`Copied: ${path.join(sourceDir, 'app.py')} -> ${path.join(destDir, 'app.py')}`);
    
    // Copy requirements.txt
    fs.copyFileSync(path.join(sourceDir, 'requirements.txt'), path.join(destDir, 'requirements.txt'));
    console.log(`Copied: ${path.join(sourceDir, 'requirements.txt')} -> ${path.join(destDir, 'requirements.txt')}`);
    
    // Copy directories
    const dirs = ['transformers', 'utils', 'rules', 'templates', 'static'];
    for (const dir of dirs) {
        copyDir(path.join(sourceDir, dir), path.join(destDir, dir));
    }
    
    console.log('Python backend files copied successfully!');
} catch (error) {
    console.error('Error copying files:', error);
} 