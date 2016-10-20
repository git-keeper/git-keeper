/**
 * This class implements the strategy that always cooperates.
 * 
 * @author mebjc01
 */
public class AlwaysCooperate implements Strategy
{
    /**
     * Get the play for a current round
     * @return 'c' always
     */
    public char play()
    {
        return 'c';
    }

    /**
     * report the result of the previous round
     * @param opponentChoice 'c' or 'd' based on the opponent's play
     */
    public void report(char opponentChoice)
    {

    }

    /**
     * Reset the strategy for a new game
     */
    public void reset()
    {

    }

    /**
     * Get the name of this strategy
     * @return "AlwaysCooperate"
     */
    public String getName()
    {
        return "AlwaysCooperate";
    }
}
