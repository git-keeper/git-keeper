/**
 * This interface defines the requirements for any strategy
 *
 * @author mebjc01
 */
public interface Strategy {
    /**
     * Get the play for the current round
     *
     * @return 'c' or 'd'
     */
    public char play();

    /**
     * report the result of the previous round
     *
     * @param opponentChoice 'c' or 'd' based on the opponent's play
     */
    public void report(char opponentChoice);

    /**
     * reset the strategy for a new game
     */
    public void reset();

    /**
     * Get the name of the strategy
     *
     * @return a unique identifiable name
     */
    public String getName();
}
