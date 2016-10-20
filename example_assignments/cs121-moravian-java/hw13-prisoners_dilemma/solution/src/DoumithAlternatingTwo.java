/**
 * This class impletements the DoumithAlternatingTwo strategy.
 * It Continiously changes from Defect to Cooperate each turn.
 * It is similiar to the DoumithAlternating Strategy except it Defects first
 * then changes from cooperates to defect each turn
 * @author Aziz Doumith
 */
public class DoumithAlternatingTwo implements Strategy
{
    int numRounds;

    /**
     * Creates a new DoumithAlternatingTwo strategy
     */
    public DoumithAlternatingTwo()
    {
        numRounds = 0;

    }

    /**
     * Get the play for the current round
     * @return 'c' or 'd' based on the opponent's previous play
     */
    public char play()
    {
        /* For the first round we defecting, then we continiously change
         * between cooperating and defecting. By modding the numRounds by 2
         * the odd numbered rounds will cooperate and even numbered rounds will
         * defect
         */

        if (numRounds % 2 == 0)
        {
            numRounds += 1;
            return 'd';
        }
        //else
        numRounds += 1;
        return 'c';
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
     * @return "DoumithAlternatingTwo"
     */
    public String getName()
    {
        return "DoumithAlternatingTwo";
    }
}

