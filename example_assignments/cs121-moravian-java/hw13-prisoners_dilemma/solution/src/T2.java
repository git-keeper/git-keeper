/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author torres
 */
public class T2 implements Strategy
{

    private String name;
    private char opponentChoice;
    /** Initializes the the name of the strategy.
     * and resets T2 to default values.
     */
    public T2()
    {
        this.name = "T2";
        this.reset();
    }

    /** Plays the appropriate move for T2
     *
     * @return a char 'c'
     */
    public char play()
    {
      return opponentChoice;
    }

    /** Reports the action to the opponent.
     *
     * @param opponentChoice of either char 'c' or 'd'
     */
    public void report(char opponentChoice)
    {
        this.opponentChoice = opponentChoice;
    }

    /** Resets the strategy T2 to it's default state.
     *
     */
    public void reset()
    {
        this.opponentChoice='d';
    }

    /** Gets the name of the strategy.
     *
     * @return a string of the strategy which is AlwaysCooperate
     */
    public String getName()
    {
        return name;
    }

}