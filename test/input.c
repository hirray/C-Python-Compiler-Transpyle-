#include <stdio.h>

// Function to check even or odd
int checkEven(int num) {
    if (num % 2 == 0) {
        return 1;
    } else {
        return 0;
    }
}

int main() {

    int n = 4;
    int result;

    // Function call
    result = checkEven(n);

    // If-else using function result
    if (result == 1) {
        printf("Number is even\n");
    } else {
        printf("Number is odd\n");
    }

    // For loop with condition
    for (int i = 1; i <= 5; i++) {
        printf("Value: %d\n", i);
    }

    // While loop
    while (n > 0) {
        n--;
    }

    return 0;
}