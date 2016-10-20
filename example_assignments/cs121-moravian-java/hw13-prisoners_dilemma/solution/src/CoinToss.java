import java.util.Random;

/**
 * Created by McDonaldDylan13 on 4/1/2016.
 */

public class CoinToss implements Strategy {
    @Override
    public char play() {
        int n =  (int) (Math.random()* 2 + 1);
        if (n == 1.0){
            return 'c';
        }
        else{
            return 'd';
        }
    }

    @Override
    public void report(char opponentChoice) {

    }

    @Override
    public void reset() {

    }

    @Override
    public String getName() {
        return "Coin Toss";
    }
}
