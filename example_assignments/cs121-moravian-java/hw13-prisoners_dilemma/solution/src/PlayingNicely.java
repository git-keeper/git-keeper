
public class PlayingNicely implements Strategy {
    int opponentCoopNum = 0;
    int opponentDefNum = 0;

    @Override
    public char play() {
        if (opponentDefNum > opponentCoopNum){
            return 'd';
        }
        return 'c';
    }

    @Override
    public void report(char opponentChoice) {
        if (opponentChoice == 'd'){
            opponentDefNum += 1;
        }

        if (opponentChoice == 'c'){
            opponentCoopNum += 1;
        }


    }

    @Override
    public void reset() {
        opponentCoopNum = 0;
        opponentDefNum = 0;

    }

    @Override
    public String getName() {
        return "PlayingNicely";
    }
}
