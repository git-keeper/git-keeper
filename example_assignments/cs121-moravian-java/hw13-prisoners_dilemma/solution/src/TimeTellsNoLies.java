/**
 * Created by andrew on 4/2/16.
 */
public class TimeTellsNoLies implements Strategy{
    private int interrogations = 0;
    private int years = 0;
    private int average = 0;
    private char oppChoice;
    private char selfChoice;

    /**
     * plays through one round of the scenario
     * @return
     */
    @Override
    public char play() {
        if (oppChoice == 'c') {
            if (selfChoice == 'c') {
                years += .5;
            }
        }
        if (oppChoice == 'd') {
            if (selfChoice == 'c') {
                years += 10;
            }
            if (selfChoice == 'd') {
                years += 5;
            }
        }
        interrogations += 1;
        average = years/interrogations;
        if (average >= 5) {
            selfChoice = 'd';
            return 'd';
        }
        else {
            selfChoice = 'c';
            return 'c';
        }
    }

    /**
     * declares what the opponent's choice last round was
     * @param opponentChoice 'c' or 'd' based on the opponent's play
     */
    @Override
    public void report(char opponentChoice) {
        oppChoice = opponentChoice;
    }

    /**
     * resets all variables, in order to start a new round
     */
    @Override
    public void reset() {
        interrogations = 0;
        years = 0;
        average = 0;
        oppChoice = 'a';
        selfChoice = 'a';
    }

    /**
     * gives the name of the strategy
     * @return
     */
    @Override
    public String getName() {
        return "TimeTellsNoLies";
    }
}
