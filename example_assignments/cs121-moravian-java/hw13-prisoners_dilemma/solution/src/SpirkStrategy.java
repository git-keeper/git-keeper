public class SpirkStrategy implements Strategy {
    private char opponentsPlay = 'd';

    public SpirkStrategy() {
        reset();
    }

    @Override
    public char play() {
        if (opponentsPlay == 'd') {
            return 'c';
        }
        else
            return 'd';
    }

    @Override
    public void report(char opponentChoice) {
        opponentsPlay = opponentChoice;
    }

    @Override
    public void reset() {
        opponentsPlay = 'd';
    }

    @Override
    public String getName() {
        return "SpirkStrategy";
    }
}

//do the opposite of what they did last turn