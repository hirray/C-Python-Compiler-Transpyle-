def add(a, b):
    return a + b
def check(n):
    if n >= 0:
        return 1
    else:
        return 0
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result = result * i
    return result
a = 5
b = 10
num = -3
sumResult = None
factResult = None
sumResult = add(a, b)
factResult = factorial(5)
if check(num):
    print("Number is Positive")
else:
    print("Number is Negative")
if a < b:
    if b > 5:
        print("Nested condition true")
    else:
        print("Inner else")
for i in range(1, 5 + 1):
    if i % 2 == 0:
        print("Even")
    else:
        print("Odd")
while num < 0:
    num += 1
x = 5
while x > 0:
    print(f"{x}")
    x -= 1
print(f"Sum: {sumResult}")
print(f"Factorial: {factResult}")