public class DoWhatItDo implements Strategy {
    private char whatToDo;
    private int count;
    private int numDefects;

    public DoWhatItDo() {
        reset();
    }

    @Override
    public char play() {
        return whatToDo;
    }

    @Override
    public void report(char opponentChoice) {
        if (opponentChoice == 'd')
            numDefects += 1;
        if (numDefects > 0 && count < 2 * numDefects) {
            whatToDo = 'd';
            count += 1;
        }
        else
            whatToDo = 'c';
    }

    @Override
    public void reset() {
        whatToDo = 'c';
    }

    @Override
    public String getName() {
        return "DoWhatItDo";
    }
}
