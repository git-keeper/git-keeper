/**
 * This Strategy starts off by always defecting.  The next myDecision will also
 * be defect.  Then if the counter mod 3 = 0, myDecision will be randomized.  
 * If the counter mod 4 = 0, myDecision will also be randomized.
 * @author The Shawn Sylvainus
 */
public class TerrellStrategy implements Strategy
{
    private char myDecision;
    private int count;
    
    /**
     * The constructor for this class creates a new TerrellStrategy.
     */
    public TerrellStrategy()
    {
        myDecision = 'D';
        count = 0;
    }
    
    /** 
     * This method returns the name of the strategy.
     * @return "TerrellStrategy" the name of the strategy.
     */
    public String getName()
    {
        return "TerrellStrategy";
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
        if(count % 3 == 0 || count % 4 == 0)
        {
            if(Math.random() <= 0.5)
                myDecision = 'C';
            else 
                myDecision = 'D';
        }
            
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
