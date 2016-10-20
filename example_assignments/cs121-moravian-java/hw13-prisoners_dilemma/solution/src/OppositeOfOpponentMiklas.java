
public class OppositeOfOpponentMiklas implements Strategy{
    private char opponentLastPlay;
    private char oppositeLastPlay;

    public OppositeOfOpponentMiklas(){
        reset();
    }


    @Override
    public char play() {
        return oppositeLastPlay;
    }

    @Override
    public void report(char opponentChoice) {
        opponentLastPlay = opponentChoice;
        if ('c' == opponentLastPlay){
            oppositeLastPlay = 'd';
        }
        if ('d' == opponentLastPlay){
            oppositeLastPlay = 'c';
        }


    }

    @Override
    public void reset() {
        opponentLastPlay = 'c';

    }

    @Override
    public String getName() {
        return "OppositeOfOpponentMiklas";
    }
}
