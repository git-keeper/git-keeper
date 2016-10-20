public class MattDill_SimpleMajority implements Strategy {
    private int numC = 0;
    private int numD = 0;

    public char play() {
        if (numC >= numD) {return 'c';}
        else if (numD > numC) {return 'd';}
        else {return 'c';}
    }

    public void report(char opponentChoice) {
        if (opponentChoice == 'c') {numC++;}
        else if (opponentChoice == 'd') {numD++;}
    }

    public void reset() {}

    public String getName() {return "MattDill_SimpleMajority";}
}
