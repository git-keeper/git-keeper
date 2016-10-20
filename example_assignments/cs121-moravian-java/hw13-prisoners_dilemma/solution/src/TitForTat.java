/**
 * The classic tit-for-tat strategy.
 *
 * You think you can beat me!?
 * 
 * @author mebjc01
 */
public class TitForTat implements Strategy
{
    char choice;

    /**
     * Create a new tit-for-tat strategy
     */
    public TitForTat()
    {
        choice = 'c';
    }

    /**
     * Get the play for the current round
     * @return 'c' or 'd' based on the opponent's previous play
     */
    public char play()
    {
        return choice;
    }

    /**
     * report the result of the previou round
     * @param opponentChoice 'c' or 'd'  based on the opponent's play
     */
    public void report(char opponentChoice)
    {
        choice = opponentChoice;
    }

    /**
     * reset the strategy for a new game
     */
    public void reset()
    {
        choice = 'c';
    }

    /**
     * get the name of the strategy
     * @return "TitForTat"
     */
    public String getName()
    {
        return "TitForTat";
    }

}
