/**
 * Use this class to try out your printDogPairs() method.
 */
public class Main {
    public static void main(String[] args) {
        Dog[] dogs = {new Dog("John"), new Dog("Jane"), new Dog("Bob")};
        DogPairPrinter.printDogPairs(dogs);

        // The above code should print out the following:
        //
        // John and Jane
        // John and Bob
        // Jane and Bob
        //
        // Try adding some more Dog objects to the array to be sure that it
        // works with more than 3.
    }
}
