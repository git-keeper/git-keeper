
public class BackAndForth implements Strategy {
    char lastPlay = 'c';

    @Override
    public char play() {
        if (lastPlay == 'c') {
            lastPlay = 'd';
        }
        else {
            lastPlay = 'c';
        }
        return lastPlay;
    }

    @Override
    public void report(char opponentChoice) {

    }

    @Override
    public void reset() {
        lastPlay = 'c';

    }

    @Override
    public String getName() {
        return "BackAndForth";
    }
}
