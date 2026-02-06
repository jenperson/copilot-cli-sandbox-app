import os
import re
import sys
import textwrap
import time
from koyeb import Sandbox

def main():
    """Main function to run Copilot inside a Koyeb Sandbox."""
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable is not set")
        sys.exit(1)

    # Initialize sandbox
    print("=== Launching Koyeb Sandbox ===\n")
    sandbox = Sandbox.create(
        name="copilot-gradio-sandbox",
        wait_ready=True,
        idle_timeout=0,  # Keep sandbox alive indefinitely
        env={
            "GITHUB_TOKEN": GITHUB_TOKEN,
            }
    )
    print(f"✓ Sandbox created: {sandbox.name}\n")
    
    # Get filesystem and process interfaces
    fs = sandbox.filesystem
    
    try:
        # Step 1: Install dependencies
        print("Step 1: Installing dependencies...")
        result = sandbox.exec("apt-get update && apt-get install -y git curl python3-pip python3-venv", on_stdout=lambda line: print(f"[Sandbox] {line}"), on_stderr=lambda line: print(f"[Sandbox ERROR] {line}"))
        print("✓ Dependencies installed\n")
        
        # Step 2: Install Copilot CLI
        print("Step 2: Setting up Copilot CLI...")
        result = sandbox.exec("curl -fsSL https://gh.io/copilot-install | bash", on_stdout=lambda line: print(f"[Sandbox] {line}"), on_stderr=lambda line: print(f"[Sandbox ERROR] {line}"))
        if result.exit_code != 0:
            print(f"Error during Copilot CLI installation: {result.stderr}")
            return
        print("✓ Copilot CLI installed\n")
        
        # Step 3: Clone the example-gradio repository
        print("Step 3: Cloning example-gradio repository...")
        result = sandbox.exec("cd /tmp && git clone https://github.com/koyeb/example-gradio.git", on_stdout=lambda line: print(f"[Sandbox] {line}"), on_stderr=lambda line: print(f"[Sandbox ERROR] {line}"))
        if result.exit_code != 0:
            print(f"Error during repository cloning: {result.stderr}")
            return
        print("✓ Repository cloned\n")
        
        # Step 4: Install Python dependencies
        print("Step 4: Installing Python dependencies...")
        result = sandbox.exec("cd /tmp/example-gradio && pip install -r requirements.txt", on_stdout=lambda line: print(f"[Sandbox] {line}"), on_stderr=lambda line: print(f"[Sandbox ERROR] {line}"), timeout=300)
        if result.exit_code != 0:
            print(f"Error during Python dependencies installation: {result.stderr}")
            return
        print("✓ Gradio installed\n")
        
        # Step 5: Read the current app.py
        print("Step 5: Reading original application...")
        result = sandbox.exec("cat /tmp/example-gradio/app.py", on_stdout=lambda line: print(f"[Sandbox] {line}"), on_stderr=lambda line: print(f"[Sandbox ERROR] {line}"))
        original_code = result.stdout
        print("✓ Original app loaded\n")
        
        # Step 6: Use Copilot to enhance the app
        print("Step 6: Using Copilot to add a draggable list component...")
        prompt = f'''
I have this Gradio application:

{original_code}

Please enhance it by adding a new interactive component: a draggable list of programming languages (Python, JavaScript, Go).

The enhancement should:
- Add a new gr.Dropdown component with multiselect=True
- Display the three languages: Python, JavaScript, Go
- Show the current selected/reordered languages below
- Keep all existing functionality
- In demo.launch(), use: server_name="0.0.0.0", server_port=7860

Provide only the updated app.py code.
'''
        
        # Create a prompt file in the sandbox
        fs.write_file("/tmp/copilot_prompt.txt", prompt)
        
        # Use gh copilot to suggest code (or use the API if available)
        result = sandbox.exec("copilot -sp /tmp/copilot_prompt.txt")
        if result.exit_code != 0:
            print(f"Error during Copilot suggestion: {result.stderr}")
            return
        print("✓ Copilot suggestion generated\n")
        
        # Step 7: Create enhanced app.py
        # Extract Python code block from Copilot response
        copilot_response = result.stdout
        code_match = re.search(r'```python\s*(.*?)\n?```', copilot_response, re.DOTALL)
        if code_match:
            enhanced_code = textwrap.dedent(code_match.group(1))
        else:
            print("Error: Could not extract code block from Copilot response")
            return
        
        print("Step 7: Writing enhanced application...")
        fs.write_file("/tmp/example-gradio/app_enhanced.py", enhanced_code)
        print("✓ Enhanced app created\n")
        
        # Step 8: Start Gradio
        print("Step 8: Starting Gradio application...")
        port = sandbox.expose_port(7860)
        process_id = sandbox.launch_process(
            "cd /tmp/example-gradio && python3 app_enhanced.py",
            cwd="/tmp",
        )
        domain = port.exposed_at
        print(f"✓ Gradio started (process ID: {process_id})\n")
        
        # Wait for Gradio to start
        time.sleep(3)
        
        print("✓ Gradio is running on port 7860\n")
        print("📍 Your sandbox is now active with Gradio running.\n")
        print(f"Access your application through your sandbox's public URL: {domain}\n")
        
        # Keep sandbox alive
        print("Sandbox is running. Press Ctrl+C to terminate.\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nTerminating sandbox...")
        
    finally:
        # Clean up
        print("Cleaning up resources...")
        sandbox.delete()
        print("✓ Sandbox deleted")

if __name__ == "__main__":
    main()