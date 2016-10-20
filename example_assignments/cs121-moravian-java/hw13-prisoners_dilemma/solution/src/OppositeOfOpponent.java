
public class OppositeOfOpponent implements Strategy {
    private  char opponentLastPlay;

    public OppositeOfOpponent(){

    }

    @Override
    public char play() {
        if (opponentLastPlay == 'c')
        return 'd';
        else
            return 'c';
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
        return "OppossiteOfOpponent";
    }
}
