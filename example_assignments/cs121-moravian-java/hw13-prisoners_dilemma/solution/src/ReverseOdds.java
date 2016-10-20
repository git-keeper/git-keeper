//
public class ReverseOdds implements Strategy {
    int cTally;
    int dTally;
    @Override
    public char play() {
        if (cTally >= dTally) {
            return 'd';
        }
        else {
            return 'c';
        }
    }

    @Override
    public void report(char opponentChoice) {
        if (opponentChoice == 'c') {
            cTally++;
        }
        else {
            dTally++;
        }

    }

    @Override
    public void reset() {

    }

    @Override
    public String getName() {
        return "ReverseOdds";
    }
}
