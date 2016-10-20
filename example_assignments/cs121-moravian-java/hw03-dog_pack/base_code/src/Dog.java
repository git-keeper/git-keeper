public class Dog {
    private String name;
    private String barkSound;

    public Dog(String dogName) {
        name = dogName;

        String[] barkSounds = {"bark", "ruff", "yip"};

        // i is 0 to 2 with an array of length 3
        int i = (int)(Math.random() * barkSounds.length);
        barkSound = barkSounds[i];
    }

    public void talk() {
        // random barkCount from 2 to 5
        int barkCount = (int)(Math.random() * 4) + 2;
        int count = 0;
        while (count < barkCount) {
            System.out.print(barkSound + ' ');
            count += 1;
        }
        System.out.println("my name is " + name);
    }
}
