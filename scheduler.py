import schedule
import time
import subprocess

def job():
    print("Running check_availability...")
    print("Job started at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    env_python_path = "/Users/erodm/Documents/edgarenv/bin/python"  # Adjust this path
    script_path = "/Users/erodm/Documents/cce.py"
    subprocess.run([env_python_path, script_path], check=True)
    print("Job finished at:", time.strftime("%Y-%m-%d %H:%M:%S"))

# Schedule to run every 10 minutes
schedule.every(15).minutes.do(job)

if __name__ == "__main__":
    print("Scheduler started.")  # Moved outside of the while loop
    while True:
        schedule.run_pending()
        time.sleep(1)

    