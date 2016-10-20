
public class AlwaysOpposite implements Strategy {
    private char LastPlay;
    public AlwaysOpposite(){
        reset();
    }
    @Override
    public char play() {
        if (LastPlay=='c')
            return 'd';
        return 'c';
    }

    @Override
    public void report(char opponentChoice) {
        LastPlay=opponentChoice;

    }

    @Override
    public void reset() {
        LastPlay='c';

    }

    @Override
    public String getName() {
        return "AlwaysOpposite";
    }
}
