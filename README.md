
# Copilot CLI Sandbox App

This app runs a Koyeb Sandbox that installs dependencies, clones the Gradio example app, uses the Copilot CLI to generate an enhanced `app.py`, writes it to `app_enhanced.py`, and launches the Gradio app on port 7860. It also prints the public URL for the running sandbox.

## Setup

1. Install dependencies with UV:

	```bash
	uv sync
	```

2. Export required environment variables:

	```bash
	export KOYEB_API_TOKEN="your_koyeb_api_token"
	export GITHUB_TOKEN="your_github_token"
	```

3. Run the app:

	```bash
	uv run copilot_sandbox_app.py
	```
