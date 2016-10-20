public class CooperateThenCopycat implements Strategy {
    private char opponentLastPlay;

    public CooperateThenCopycat() {
        reset();
    }

    public char play() {
        if (opponentLastPlay == '\u0000') {
            return 'c';
        }

        else {
            return opponentLastPlay;
        }
    }


    public void report(char opponentChoice) {
        opponentLastPlay = opponentChoice;
    }


    public void reset() {
        opponentLastPlay = 'c';
    }


    public String getName() {
        return "CooperateThenCopycat";
    }
}
