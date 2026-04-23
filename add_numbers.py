def add_numbers(num1, num2):
    """This function takes two numbers as input and returns their sum."""
    return num1 + num2

if __name__ == '__main__':
    number1 = float(input("Enter first number: "))
    number2 = float(input("Enter second number: "))
    print(f'The sum is: {add_numbers(number1, number2)}')