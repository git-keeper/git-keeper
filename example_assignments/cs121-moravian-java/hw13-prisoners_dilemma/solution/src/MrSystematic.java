

public class MrSystematic implements Strategy{
    private char opponentLastPlay;
    private char first= 'd';

    public char play() {
            return first;
    }


    public void report(char opponentChoice) {
        opponentLastPlay = opponentChoice;
    }


    public void reset() {
        if(opponentLastPlay=='d')
            first='c';
        else
            first='d';
    }


    public String getName() {
        return "Mr.Systematic";
    }
}
