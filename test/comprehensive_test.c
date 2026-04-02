#include <stdio.h>

// Function 1: Add two numbers
int add(int a, int b) {
    return a + b;
}

// Function 2: Check positive or negative
int check(int n) {
    if (n >= 0) {
        return 1;
    } else {
        return 0;
    }
}

// Function 3: Factorial
int factorial(int n) {
    int result = 1;

    for (int i = 1; i <= n; i++) {
        result = result * i;
    }

    return result;
}

int main() {

    // Variable declarations
    int a = 5;
    int b = 10;
    int num = -3;
    int sumResult;
    int factResult;

    // Function calls
    sumResult = add(a, b);
    factResult = factorial(5);

    // If-else with function
    if (check(num)) {
        printf("Number is Positive\n");
    } else {
        printf("Number is Negative\n");
    }

    // Nested if
    if (a < b) {
        if (b > 5) {
            printf("Nested condition true\n");
        } else {
            printf("Inner else\n");
        }
    }

    // For loop with condition inside
    for (int i = 1; i <= 5; i++) {
        if (i % 2 == 0) {
            printf("Even\n");
        } else {
            printf("Odd\n");
        }
    }

    // While loop with increment
    while (num < 0) {
        num++;
    }

    // While loop with decrement
    int x = 5;
    while (x > 0) {
        printf("%d\n", x);
        x--;
    }

    // Output results
    printf("Sum: %d\n", sumResult);
    printf("Factorial: %d\n", factResult);

    return 0;
}