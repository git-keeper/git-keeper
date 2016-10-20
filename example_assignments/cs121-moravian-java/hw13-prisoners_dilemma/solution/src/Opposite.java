/**
 * Created by Mar on 4/3/16.
 */
public class Opposite implements Strategy {

    private char opponentLastPlay;

    public Opposite(){ reset(); }

    @Override
    public char play() {
        if (opponentLastPlay == 'c') {
            return 'd';
        }

        else {
            return 'c';
        }
    }

    @Override
    public void report(char opponentChoice) {
        opponentLastPlay = opponentChoice;
    }

    @Override
    public void reset() {
        opponentLastPlay = 'c';
    }

    @Override
    public String getName() {
        return "Opposite";
    }
}
