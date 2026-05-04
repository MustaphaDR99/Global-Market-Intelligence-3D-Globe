import subprocess
import sys
import os


def run_pipeline():
    # List of scripts in execution order
    pipeline_steps = [
        "pipeline.py",
        "analytics.py",
        "predictions.py",
        "3_dimensional_globe.py"
    ]

    print("--- STARTING GLOBAL MARKET PIPELINE ---")

    for script in pipeline_steps:
        if not os.path.exists(script):
            print(f"Error: {script} not found in directory.")
            continue

        print(f"Executing: {script}...")
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"ok {script} completed successfully.")
        else:
            print(f"! Error in {script}:")
            print(result.stderr)
            break

    print("--- PIPELINE FINISHED ---")
    print("Open 'global_market_globe.html' to see the results.")


if __name__ == "__main__":
    run_pipeline()