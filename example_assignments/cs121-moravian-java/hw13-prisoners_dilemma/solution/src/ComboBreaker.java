/**
 * Created by jamesegallagher on 4/3/16.
 */
public class ComboBreaker implements Strategy {
    int counter = 0;

    public char play() {
        if (counter < 4) {
            counter += 1;
            return 'c';
        }
        double i = Math.random();
        if (i <= 0.5)
            return 'c';
        else
            return 'd';

    }


    public void report(char opponentChoice) {

    }


    public void reset() {
        counter = 0;

    }


    public String getName() {
        return "C-C-C-Combo Breaker!";
    }
}
