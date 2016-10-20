/** This strategy defects first, and then it follows the TitForTat class.
 *
 * @author Chris Kieszek
 */
public class ItsObama implements Strategy 
{

    private int games;
    private String name;
    private char enemyAction;
    
    /** Constructor initializes all variables.
     * 
     */
    public ItsObama()
    {
        games = 0;
        name = "ItsObama";
    }
    /** Will play either c or d depending on the number of games.
     * 
     * @return c or d
     */
    public char play()
    {
        if(games == 0)
        {
            games += 1;
            return 'd';
        }
        else
        {
            return enemyAction;
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

    /** Resets all the variable.
     * 
     */
    public void reset()
    {
        games = 0;
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
