import subprocess
import sys

python_executable = sys.executable

print("1. Run app")
print("2. Test model")
print("3. Run web agent")
choice = input("your choice: ")

if choice == "1":
    script_path = r"C:\Users\hatru\projectMantis_1\Model\textModel\app.py"
    subprocess.run([python_executable, script_path])
elif choice == "2":
    script_path = r"C:\Users\hatru\projectMantis_1\Model\textModel\test.py"
    subprocess.run([python_executable, script_path])
elif choice == "3":
    subprocess.run(["adk", "web", "ADK"])