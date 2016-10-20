public class STRAT implements Strategy {
    private int num = 0;
    private char opponentLastPlay;

    public STRAT() {
        reset();
    }

    @Override
    public char play() {
        num = (int)(Math.random()*3);
        if (num == 0)
            return 'c';
        else
            return 'd';

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
        return "STRAT";
    }
}