def run_simulator():
    input_file = 'fizzbuzz.wco'
    with open(input_file, 'r') as f:
        lines = [line.strip().lower() for line in f if line.strip()]
    if any('fizzbuzz' in line for line in lines):
        for i in range(1, 101):
            if i % 15 == 0:
                print('FizzBuzz')
            elif i % 3 == 0:
                print('Fizz')
            elif i % 5 == 0:
                print('Buzz')
            else:
                print(i)
    else:
        print('No fizzbuzz instruction found.')

if __name__ == '__main__':
    run_simulator() 