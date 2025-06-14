from functions.get_file_content import get_file_content

if __name__ == "__main__":
    print("Test 1:")
    result1 = get_file_content("calculator", "lorem.txt")
    print(result1)
    print("Test 2:")
    result2 = get_file_content("calculator", "main.py")
    print(result2)
    print("Test 3:")
    result3 = get_file_content("calculator", "pkg/calculator.py")
    print(result3)
    print("Test 4:")
    result4 = get_file_content("calculator", "/bin/cat")
    print(result4)