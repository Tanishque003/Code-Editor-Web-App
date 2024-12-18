import os
import subprocess
import tempfile
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def run_python_code(code):
    try:
        process = subprocess.Popen(['python3', '-c', code],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        stdout, stderr = process.communicate(timeout=10)
        return stdout, stderr, process.returncode
    except subprocess.TimeoutExpired:
        return None, "Execution timed out", 1

def run_javascript_code(code):
    try:
        process = subprocess.Popen(['node', '-e', code],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        stdout, stderr = process.communicate(timeout=10)
        return stdout, stderr, process.returncode
    except subprocess.TimeoutExpired:
        return None, "Execution timed out", 1

def run_c_code(code):
    with tempfile.TemporaryDirectory() as tmpdirname:
        source_file = os.path.join(tmpdirname, 'program.c')
        executable_file = os.path.join(tmpdirname, 'program')
        
        # Write the source code to a file
        with open(source_file, 'w') as f:
            f.write(code)
        
        # Compile the code
        compile_process = subprocess.Popen(['gcc', source_file, '-o', executable_file],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True)
        _, compile_stderr = compile_process.communicate()
        
        # If compilation fails, return the error
        if compile_process.returncode != 0:
            return None, compile_stderr, 1
        
        # Run the compiled executable
        try:
            run_process = subprocess.Popen([executable_file],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True)
            stdout, stderr = run_process.communicate(timeout=10)
            return stdout, stderr, run_process.returncode
        except subprocess.TimeoutExpired:
            return None, "Execution timed out", 1

def run_cpp_code(code):
    with tempfile.TemporaryDirectory() as tmpdirname:
        source_file = os.path.join(tmpdirname, 'program.cpp')
        executable_file = os.path.join(tmpdirname, 'program')
        
        # Write the source code to a file
        with open(source_file, 'w') as f:
            f.write(code)
        
        # Compile the code
        compile_process = subprocess.Popen(['g++', source_file, '-o', executable_file],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True)
        _, compile_stderr = compile_process.communicate()
        
        # If compilation fails, return the error
        if compile_process.returncode != 0:
            return None, compile_stderr, 1
        
        # Run the compiled executable
        try:
            run_process = subprocess.Popen([executable_file],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True)
            stdout, stderr = run_process.communicate(timeout=10)
            return stdout, stderr, run_process.returncode
        except subprocess.TimeoutExpired:
            return None, "Execution timed out", 1

def run_java_code(code):
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Find the main class name
        import re
        main_class_match = re.search(r'public\s+class\s+(\w+)', code)
        if not main_class_match:
            return None, "Could not find main class", 1
        
        main_class = main_class_match.group(1)
        source_file = os.path.join(tmpdirname, f'{main_class}.java')
        
        # Write the source code to a file
        with open(source_file, 'w') as f:
            f.write(code)
        
        # Compile the Java code
        compile_process = subprocess.Popen(['javac', source_file],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True,
                                           cwd=tmpdirname)
        _, compile_stderr = compile_process.communicate()
        
        # If compilation fails, return the error
        if compile_process.returncode != 0:
            return None, compile_stderr, 1
        
        # Run the compiled Java class
        try:
            run_process = subprocess.Popen(['java', '-cp', tmpdirname, main_class],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True)
            stdout, stderr = run_process.communicate(timeout=10)
            return stdout, stderr, run_process.returncode
        except subprocess.TimeoutExpired:
            return None, "Execution timed out", 1

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/runcode', methods=['POST'])
def run_code():
    code = request.form['code']
    language = request.form['language']

    try:
        if language == 'python':
            stdout, stderr, returncode = run_python_code(code)
        elif language == 'javascript':
            stdout, stderr, returncode = run_javascript_code(code)
        elif language == 'c':
            stdout, stderr, returncode = run_c_code(code)
        elif language == 'cpp':
            stdout, stderr, returncode = run_cpp_code(code)
        elif language == 'java':
            stdout, stderr, returncode = run_java_code(code)
        else:
            return jsonify({'output': None, 'error': 'Unsupported language'})

        if returncode == 0:
            return jsonify({'output': stdout, 'error': None})
        else:
            return jsonify({'output': None, 'error': stderr})

    except Exception as e:
        return jsonify({'output': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5500)