from functions.run_python import run_python_file

if __name__ == "__main__":
    print("Test 1:")
    result1 = run_python_file("calculator", "main.py")
    print(result1)
    print("Test 2:")
    result2 = run_python_file("calculator", "tests.py")
    print(result2)
    print("Test 3:")
    result3 = run_python_file("calculator", "../main.py")
    print(result3)
    print("Test 4:")
    result4 = run_python_file("calculator", "nonexistent.py")
    print(result4)