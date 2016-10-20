public class Dog {
    private String name;

    public Dog(String dogName) {
        name = dogName;
    }

    public String getName() {
        return name;
    }

    public void talk() {
        System.out.println("Bark bark, my name is " + name);
    }
}
