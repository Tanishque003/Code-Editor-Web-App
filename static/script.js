let editor;

document.addEventListener('DOMContentLoaded', () => {
    const languageSelect = document.getElementById('language-select');
    const themeSelect = document.getElementById('theme-select');
    
    // Initialize CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
        lineNumbers: true,
        mode: "python",
        theme: "default",
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        extraKeys: {
            "Tab": "indentMore",
            "Shift-Tab": "indentLess"
        }
    });

    // Language mode mapping
    const languageModes = {
        'python': 'python',
        'javascript': 'javascript',
        'c': 'text/x-csrc',
        'cpp': 'text/x-c++src',
        'java': 'text/x-java'
    };

    // Language switching
    languageSelect.addEventListener('change', (e) => {
        const selectedLanguage = e.target.value;
        
        // Change CodeMirror mode based on language
        editor.setOption('mode', languageModes[selectedLanguage]);
        
        // Set default template for each language
        setLanguageTemplate(selectedLanguage);
    });

    // Theme switching
    themeSelect.addEventListener('change', (e) => {
        const selectedTheme = e.target.value;
        editor.setOption('theme', selectedTheme);
    });

    // Set initial template
    setLanguageTemplate('python');
});

function setLanguageTemplate(language) {
    const templates = {
        'python': `# Python Code
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()`,
        'javascript': `// JavaScript Code
function main() {
    console.log("Hello, World!");
}

main();`,
        'c': `#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}`,
        'cpp': `#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}`,
        'java': `public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}`
    };

    editor.setValue(templates[language] || '');
}

function clearEditor() {
    editor.setValue('');
    document.getElementById('output').innerHTML = '';
}

function runCode() {
    const code = editor.getValue();
    const language = document.getElementById('language-select').value;
    const outputDiv = document.getElementById('output');

    // Clear previous output
    outputDiv.innerHTML = '<div class="loading">Running code...</div>';

    // Send code to server
    fetch('/runcode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `code=${encodeURIComponent(code)}&language=${encodeURIComponent(language)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.output) {
            outputDiv.innerHTML = `<pre class="output success">${escapeHtml(data.output)}</pre>`;
        } else if (data.error) {
            outputDiv.innerHTML = `<pre class="output error">${escapeHtml(data.error)}</pre>`;
        }
    })
    .catch(error => {
        outputDiv.innerHTML = `<pre class="output error">Error: ${escapeHtml(error.message)}</pre>`;
    });
}

// Utility function to escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }