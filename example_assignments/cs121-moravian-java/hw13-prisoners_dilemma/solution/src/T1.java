/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author torres
 */
public class T1 implements Strategy
{

    private String name;
    private int dCounter;
    private char opponentChoice;
    private int round;
    /** Initializes the the name of the strategy.
     * and resets T1 to default values.
     */
    public T1()
    {
        this.name = "T1";
        this.reset();
    }

    /** Plays the appropriate move for T1
     *
     * @return a char 'c' or 'd'
     */
    public char play()
    {
        if(this.dCounter > 1 && round%2 != 0){
            this.dCounter = 0;
            return 'c';
        }
        if(this.dCounter > 1 && round%2 != 0){
            this.dCounter = 0;
            return 'd';
        }
        
        else{
            this.dCounter += 1;
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
        this.round = 0;
        //Keeps track of how many times d is used by this strat
        this.dCounter = 0;
        this.opponentChoice=' ';
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

