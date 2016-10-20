/**
 * This class implements the strategy that always defects
 *
 * @author mebjc01
 */
public class AlwaysDefect implements Strategy {
    /**
     * Get the play for the current round
     *
     * @return 'd' always
     */
    public char play() {
        return 'd';
    }

    /**
     * report the result of the previous round
     *
     * @param opponentChoice 'c' or 'd' based on the opponent's play
     */
    public void report(char opponentChoice) {

    }

    /**
     * Reset the strategy for a new game
     */
    public void reset() {

    }

    /**
     * Get the name of this strategy
     *
     * @return "AlwaysDefect"
     */
    public String getName() {
        return "AlwaysDefect";
    }

}
