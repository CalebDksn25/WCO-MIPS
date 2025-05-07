

int main() {
    int i = 1;
    int a = 15;
    int b = 5;
    int c = 3;
    int d = 73;
    for (i;i<=100; i++) {
        if (i % a == 0) {
            printf("WCO\n");
        } else if (i % b == 0) {
            printf("W\n");
        } else if (i % c == 0) {
            printf("C\n");
        } else if (i % d == 0) {
            printf("O\n");
        } else {
            printf("%d\n", i);
        }
    }
    return 0;
}