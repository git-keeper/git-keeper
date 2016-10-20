/**
 * Created by alexisthiel on 4/1/16.
 */
public class AktStrategy implements Strategy {

    private int numCooperate;
    private int numDefect;

    public AktStrategy(){
        reset();
    }

    @Override
    public char play() {
        if(numCooperate > (3 * numDefect))
            return 'c';
        if (numCooperate > numDefect)
            return 'd';
        else
            return 'c';
    }

    @Override
    public void report(char opponentChoice) {
        if (opponentChoice == 'c')
            numCooperate += 1;
        if (opponentChoice == 'd')
            numDefect += 1;
    }

    @Override
    public void reset() {
        numCooperate = 0;
        numDefect = 0;
    }

    @Override
    public String getName() {
        return "AKT Strategy";
    }
}
