// author = Zach Balga
public class MultipleOf3Coorp implements Strategy{
    private int count = 0;

    public MultipleOf3Coorp() {
        reset();
    }

    @Override
    public char play() {
        char choice = 'd';
        if (count % 3 == 0) {
            choice = 'c';
            return choice;
        }
        else {
            choice = 'd';
            return choice;
        }

    }

    @Override
    public void report(char opponentChoice) {
    }

    @Override
    public void reset() {
        count += 1;

    }

    @Override
    public String getName() {
        return "MultipleOf3Coorp";
    }
}
