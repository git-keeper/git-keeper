import java.util.Random;

public class TitForTatMeetsRandom implements Strategy {
    private char opponentLastPlay;

    public TitForTatMeetsRandom() {
        reset();
    }


    @Override
    public char play() {
        double x = Math.random();
        if (opponentLastPlay != 'c') {
            if (x < 0.5) {
                opponentLastPlay = 'd';
            }
            else {
                opponentLastPlay = 'c';
            }
        }
        return opponentLastPlay;
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
        return "To Defect Or To Randomize";
    }
}
