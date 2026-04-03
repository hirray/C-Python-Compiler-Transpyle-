#include <stdio.h>
int main() {
    float target = 3.14159f;
    float *ptr = &target;
    *ptr = 600.0f;
    printf("Floats: %.2f, %.8f\n", target, *ptr);
    return 0;
}