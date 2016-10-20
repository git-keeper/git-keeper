/**
 * This class impletements the DoumithAlternating strategy.
 * It Continiously changes from Cooperate to Defect each turn
 * @author Aziz Doumith
 */
public class DoumithAlternating implements Strategy
{
    int numRounds;
    
    /**
     * Creates a new DoumithAlternating strategy
     */
    public DoumithAlternating()
    {
        numRounds = 0;

    }

    /**
     * Get the play for the current round
     * @return 'c' or 'd' based on the opponent's previous play
     */
    public char play()
    {
        /* For the first round we cooperating, then we continiously change
         * between defect and cooperating. By modding the numRounds by 2
         * the odd numbered rounds will defect and even numbered rounds will
         * cooperate
         */

        if (numRounds % 2 == 0)
        {
            numRounds += 1;
            return 'c';
        }
        //else
        numRounds += 1;
        return 'd';
    }

    /**
     * Report the result of the previous round
     * @param opponentChoice - 'c' or 'd' based on the opponent's play
     */
    public void report(char opponentChoice)
    {
        /*
         * This simply returns because we dont need to return anything
         * because this strategy alternates no matter the opponnent's choice.
         */
        return;
    }

    /**
     * Reset the strategy for a new game
     */
    public void reset()
    {
        /*
         * This simply returns because we dont need to reset anything
         * because this strategy alternates no matter what.
         */
        return;
    }

    /**
     * Get the name of the strategy
     * @return "DoumithAlternating"
     */
    public String getName()
    {
        return "DoumithAlternating";
    }
}

