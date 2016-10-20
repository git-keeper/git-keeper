
public class RandomSelection implements Strategy {

    @Override
    public char play() {
        double result = Math.random();
        if (result < .5) {
            return 'c';
        }
        else {
            return 'd';
        }

    }

    @Override
    public void report(char opponentChoice) {

    }

    @Override
    public void reset() {

    }

    @Override
    public String getName() {
        return "RandomSelection";
    }
}
