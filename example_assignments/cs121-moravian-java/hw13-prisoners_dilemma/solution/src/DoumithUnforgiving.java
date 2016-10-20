/**
 * This class implements the DoumithUnforgiven. This Strategy cooperates
 * until the opponent defects, after which it defects for the rest of the Game.
 * @author Aziz Doumith
 */
public class DoumithUnforgiving implements Strategy
{

    private boolean opponentDefected;

    /**
     * Creates a new DoumithUnforgivingStrategy
     */
    public DoumithUnforgiving()
    {
        opponentDefected = false;
    }

    /**
     * Get the play for the current round
     * @return 'c' or 'd' based on the opponent's previous play
     */
    public char play()
    {
        /* We cooperate until the opponent defects, then we always defect
         */
        if (opponentDefected)
        {
            return 'd';
        }

        //else we cooperate
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
            opponentDefected = true;
        }

        //else we do not need to do anything because we will cooperate
        return;
    }
     

    /**
     * Reset the strategy for a new game
     */
    public void reset()
    {
        opponentDefected = false;
    }

    /**
     * Get the name of the strategy
     * @return "DoumithUnforgiving"
     */
    public String getName()
    {
        return "DoumithUnforgiving";
    }

}
