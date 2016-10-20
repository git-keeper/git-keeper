public class DogPack {
    private Dog[] dogs;

    public DogPack(String[] dogNames) {
        // Complete this constructor.

        // Initialize the dogs array to be a new array that is the same
        // length as dogNames.
        dogs = new Dog[dogNames.length];

        // Use a loop to initialize each Dog in the dogs array
        // to a new Dog. Each Dog in dogs should have the corresponding name
        // in the parallel dogNames array.
        int i = 0;
        while (i < dogNames.length) {
            dogs[i] = new Dog(dogNames[i]);
            i += 1;
        }
    }

    public void makeRuckus() {
        // Complete this function.

        // Use a loop to make each dog talk.
        int i = 0;
        while (i < dogs.length) {
            dogs[i].talk();
            i += 1;
        }
    }
}
