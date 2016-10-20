public class HAUUUUG implements Strategy {
    private int answerC = 0;
    private int answerD = 0;
    private int turn = 0;
    private char answer = 'd';

    @Override
    public char play() {
        return answer;
    }

    @Override
    public void report(char opponentChoice) {

        if (opponentChoice == 'c') {answerC += 1;}

        if (opponentChoice == 'd') {answerD += 1;}

        if (turn < 4) {
            if (opponentChoice == 'c') {
                answer = 'd';
            }

            else {
                answer = 'c';
            }

            turn += 1;
        }

        if (turn == 4) {
            if (answerC > answerD) {
                answer = 'd';
                turn = 0;
            }

            else {
                answer = 'd';
                turn = 0;
            }
        }
    }

    @Override
    public void reset() {

        answerC = 0;
        answerD = 0;
        turn = 0;
        answer = 'd';

    }

    @Override
    public String getName() {
        return "HAUUUUG";
    }
}
