/** Strategy defects the first round, and then, depending on how many cooperates
 * and defects the enemy has done, will determine what the player will choose
 * next.
 * @author Chris Kieszek
 */
public class FiveGirlsPregnentAndCounting implements Strategy
{

    private int moves;
    private int actionC;
    private int actionD;
    private String name;
    private char enemyAction;
    
    /** Constructor initializes all variables.
     * 
     */
    public FiveGirlsPregnentAndCounting()
    {
        name = "FiveGirlsPregnentAndCounting";
        actionC = 0;
        actionD = 0;
        moves = 0;
    }
    /** Will play either c or d depending on the number of moves and 
     * number of c's and d's.
     * 
     * @return c or d
     */
    public char play()
    {
        if(moves >= 1 && actionD < actionC)
        {
            actionD += 1;
            return 'd';
        }
        else if(moves >= 1 && actionC == actionD)
        {
            actionC += 1;
            return enemyAction;
        }
        else if(moves < 1)
        {
            moves += 1;
            return 'd';
        }
        else
        {
            actionC += 1;
            return 'c';
        }
    }
    /** Reports the enemy action.\
     * 
     * @param opponentChoice which is either c or d
     */
    public void report(char opponentChoice)
    {
        enemyAction = opponentChoice;
    }

    /** Resets all the variables.
     * 
     */
    public void reset()
    {
        actionC = 0;
        actionD = 0;
        moves = 0;
    }

    /** Gets the name of the strategy.
     * 
     * @return name of strategy
     */
    public String getName()
    {
        return name;
    }

}
