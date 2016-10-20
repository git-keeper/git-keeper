/**
 * This class impletements the DoumithTitForTatWithForgiveness strategy.
 * It is similiar to TitForTat except that opponent must defect more than 
 * twice before it acts as a regular TitForTat Strategy
 * @author Aziz Doumith
 */
public class DoumithTitForTatWithForgiveness implements Strategy
{

    private char opponentChoice;
    private int numOpponentDefects;

    /**
     * Creates a new DoumithTitForTatWithForgiveness strategy
     */
    public DoumithTitForTatWithForgiveness()
    {
        opponentChoice = ' ';
        numOpponentDefects = 0;

    }

    /**
     * Get the play for the current round
     * @return 'c' or 'd' based on the opponent's previous play
     */
    public char play()
    {
        /* For the first round we cooperate, after that we do whatever our
         * opponents last choice was if they defected more than
         * twice in the game.
         */
        if (numOpponentDefects > 2)
        {
            return opponentChoice;
        }
        //else
        return 'c';
    }

    /**
     * Report the result of the previous round
     * @param opponentChoice 'c' or 'd' based on the opponent's play
     */
    public void report(char opponentChoice)
    {
        if (opponentChoice == 'd')
        {
            numOpponentDefects += 1;
        }

        this.opponentChoice = opponentChoice;
    }

    /**
     * Reset the strategy for a new game
     */
    public void reset()
    {
        numOpponentDefects = 0;
        opponentChoice = ' ';
    }

    /**
     * Get the name of the strategy
     * @return "DoumithTitForTatWithForgiveness"
     */
    public String getName()
    {
        return "DoumithTitForTatWithForgiveness";
    }
}
