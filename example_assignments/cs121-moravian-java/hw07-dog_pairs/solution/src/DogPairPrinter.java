/**
 * This class provides a static method which prints out all possible pairs of Dog
 * names from an array of Dog references. No Dog should be paired with itself
 * and each Dog should be paired with each other Dog only once.
 */
public class DogPairPrinter {
    public static void printDogPairs(Dog[] dogs) {
        for (int i = 0; i < dogs.length - 1; i++) {
            for (int j = i + 1; j < dogs.length; j++) {
                System.out.println(dogs[i].getName() + " and " + dogs[j].getName());
            }
        }
    }
}
