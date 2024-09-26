from flask import Flask
from flask_socketio import SocketIO, emit
import sys
import io
import os  # Add the os module to get environment variables

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')  # Set async_mode to 'eventlet'

# Keep track of the code and input state
execution_context = {
    'code': '',               # Code to execute
    'waiting_for_input': False, # Track if waiting for input
    'input_value': None        # Store user input
}

# Custom input handler that pauses execution and sends a prompt to the frontend
def input_handler(prompt):
    execution_context['waiting_for_input'] = True  # Set waiting for input
    emit('prompt', prompt)  # Send prompt to frontend
    socketio.sleep(1)  # Pause execution

# Function to execute Python code step by step
def execute_python_code():
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    try:
        # Execute the code stored in execution_context
        exec(execution_context['code'], globals())  # Execute code
        return redirected_output.getvalue()  # Return output
    except Exception as e:
        return str(e)  # Return any errors
    finally:
        sys.stdout = old_stdout  # Reset stdout

# Handle input event (when Python code is sent)
@socketio.on('input')
def handle_code(data):
    execution_context['code'] = data  # Store the Python code to be executed
    globals()['input'] = input_handler  # Override input() with custom handler
    result = execute_python_code()  # Execute the code
    emit('output', result)  # Send the result to the frontend

# Handle user input (sent from the frontend)
@socketio.on('user_input')
def handle_user_input(user_data):
    if execution_context['waiting_for_input']:
        execution_context['waiting_for_input'] = False  # Stop waiting for input
        execution_context['input_value'] = user_data  # Store user input

        # Resume execution by setting input() to return the user input
        globals()['input'] = lambda _: execution_context['input_value']

        result = execute_python_code()  # Resume execution
        emit('output', result)  # Send output to frontend

# Update this part for production deployment
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get port from environment variable, fallback to 5000
    socketio.run(app, host='0.0.0.0', port=port)  # Listen on all interfaces, use Railway's port