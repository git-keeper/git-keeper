/**
 * Created by johngleason on 4/3/16.
 */
public class Odds implements Strategy {
    int cTally;
    int dTally;
    @Override
    public char play() {
        if (cTally >= dTally) {
            return 'c';
        }
        else {
            return 'd';
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
        return "Odds";
    }
}
