def checkEven(num):
    if num % 2 == 0:
        return 1
    else:
        return 0
n = 4
result = None
result = checkEven(n)
if result == 1:
    print("Number is even")
else:
    print("Number is odd")
for i in range(1, 5 + 1):
    print(f"Value: {i}")
while n > 0:
    n -= 1