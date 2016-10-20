/*

Implement this class so that it prints out all the powers of 2 less than
1 million using a loop. You will need to create a main() function.

The first part of the output should look like this:
1
2
4
8
16
...

Remember, there is no exponentiation operator ** like there is in Python. You will
have to double the current power each time.

*/

public class PowersOf2 {
    public static void main(String args[]) {
        int pow = 1;

        while (pow < 1000000) {
            System.out.println(pow);
            pow *= 2;
        }
    }
}
