

int main() {
    int i = 1;
    int a = 15;
    int b = 5;
    int c = 3;
    for (i;i<=100; i++) {
        if (i % a == 0) {
            printf("FizzBuzz\n");
        } else if (i % b == 0) {
            printf("Fizz\n");
        } else if (i % c == 0) {
            printf("Buzz\n");
        } else {
            printf("%d\n", i);
        }
    }
    return 0;
}