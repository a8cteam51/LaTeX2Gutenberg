#!/usr/bin/env python3
"""Convert a LaTeX file and preview the result in WordPress via wp-playground/cli.

Usage:
    python preview.py <input.tex>

This script:
1. Runs latex2wp.py to convert the .tex file to Gutenberg HTML
2. Writes a blueprint.json that inserts the output as a post
3. Starts a local WordPress instance with @wp-playground/cli
"""

import sys
import os
import json
import base64
import subprocess
import webbrowser
import threading
import time


def main():
    if len(sys.argv) < 2:
        print("Usage: python preview.py <input.tex>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace(".tex", ".html")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    blueprint_path = os.path.join(project_dir, "blueprint.json")

    # Run the converter
    subprocess.run([sys.executable, "latex2wp.py", input_file], check=True)

    # Read the output
    with open(output_file) as f:
        html_content = f.read()

    # Base64-encode content for safe embedding in PHP strings
    content_b64 = base64.b64encode(html_content.encode()).decode()

    php_code = (
        "<?php require '/wordpress/wp-load.php'; "
        "$content = base64_decode('" + content_b64 + "'); "
        "kses_remove_filters(); "
        "wp_update_post(wp_slash(["
        "'ID' => 1, "
        "'post_title' => 'LaTeX Preview', "
        "'post_content' => $content, "
        "'post_status' => 'publish'"
        "])); "
        "kses_init_filters(); "
        "?>"
    )

    blueprint = {
        "landingPage": "/?p=1",
        "steps": [
            {"step": "login"},
            {"step": "runPHP", "code": php_code},
        ],
    }

    with open(blueprint_path, "w") as f:
        json.dump(blueprint, f, indent=2)
    print("Wrote " + blueprint_path)

    # Auto-open browser after a short delay
    def open_browser():
        time.sleep(5)
        webbrowser.open("http://127.0.0.1:9400/?p=1")

    threading.Thread(target=open_browser, daemon=True).start()

    # Start @wp-playground/cli server with the blueprint
    print("Starting WordPress Playground... (Ctrl+C to stop)")
    try:
        subprocess.run(
            ["npx", "@wp-playground/cli", "server",
             "--blueprint=" + blueprint_path],
            cwd=project_dir,
        )
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
