import java.util.ArrayList;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        ArrayList<Dog> dogs = new ArrayList<>();

        String prompt = "Enter a name for a dog (enter nothing to stop): ";

        System.out.print(prompt);
        String name = sc.nextLine();

        while (!name.equals("")) {
            dogs.add(new Dog(name));
            System.out.print(prompt);
            name = sc.nextLine();
        }

        for (Dog dog : dogs) {
            dog.talk();
        }
    }
}
