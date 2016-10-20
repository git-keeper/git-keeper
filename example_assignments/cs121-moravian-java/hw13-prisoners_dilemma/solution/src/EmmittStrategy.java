/**
 * This Strategy is going to start by defecting, and then it will always 
 * defect until the counter mod 3 = 0.  When the counter mod 3 = 0 myDecison
 * returns cooporate.
 * @author The Shawn Sylvainus
 */
public class EmmittStrategy implements Strategy 
{
    private char myDecision;
    private int count;
    
    /**
     * The constructor for this class creates a new EmmittStrategy.
     */
    public EmmittStrategy()
    {
        myDecision = 'D';
        count = 0;
    }
    
    /** 
     * This method returns the name of the strategy.
     * @return "EmmittStrategy" the name of the strategy.
     */
    public String getName()
    {
        return "EmmittStrategy";
    }
    
    /**
     * This method returns the decision the strategy makes for one turn.
     * @return 'myDecision' the decision for this strategy.
     */
    public char play()
    {
        return myDecision;
    }
    
     /**
     * This method is where the logic of the strategy is.
     * @param opponentChoice the choice of opponent last round.
     */
    public void report(char opponentChoice)
    {
        if(count % 3 == 0)
            myDecision = 'C';
        else
            myDecision = 'D';
        
        count++;
    }
    
    
     /**
     * This method resets any variables that need to be reset.
     */
    public void reset()
    {
    }
}
