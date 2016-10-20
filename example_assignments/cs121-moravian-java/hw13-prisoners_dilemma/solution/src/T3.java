/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author torres
 */
public class T3 implements Strategy{

    private String name;
    private char opponentChoice;
    private int cCounter;
    /** Initializes the the name of the strategy.
     * and resets T1 to default values.
     */
    public T3()
    {
        this.name = "T3";
        this.reset();
    }

    /** Plays the appropriate move for T3
     *
     * @return a char 'c' or 'd'
     */
    public char play()
    {
        if(this.cCounter > 1){
            this.cCounter = 0;
            return 'c';
        }
        
        else{
            this.cCounter += 1;
            return 'd';
        }
    }

    /** Reports the action to the opponent.
     *
     * @param opponentChoice of either char 'c' or 'd'
     */
    public void report(char opponentChoice)
    {
        this.opponentChoice = opponentChoice;
    }

    /** Resets the strategy T1 to it's default state.
     *
     */
    public void reset()
    {
        this.cCounter = 0;
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