public class AlwaysChange implements Strategy{
    private char opponentLastPlay;

    public AlwaysChange(){
        reset();
    }

    @Override
    public char play() {
        return opponentLastPlay;
    }

    @Override
    public void report(char opponentChoice) {
        if(opponentChoice == 'c')
            opponentLastPlay = 'd';
        else{
            opponentLastPlay = 'c';
        }
    }

    @Override
    public void reset() {
    }

    @Override
    public String getName() {
        return "AlwaysChange";
    }
}
