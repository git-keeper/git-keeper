/**
 * This class represents a match between two strategies.
 * 
 * @author mebjc01
 */
public class Match
{
    private final int NUMGAMES = 1000;
    private final int NUMTURNS = 100;
    
    private Strategy s1;
    private Strategy s2;

    private double s1Avg;
    private double s2Avg;

    private boolean ran;

    /**
     * Create a new match between two strategies
     * @param s1 the first strategy
     * @param s2 the scond strategy
     * @throws IllegalArgumentException if either strategy is null
     */
    public Match(Strategy s1, Strategy s2)
    {
        if(s1 == null)
            throw new IllegalArgumentException("s1 is null");
        if(s2 == null)
            throw new IllegalArgumentException("s2 is null");
        
        this.s1 = s1;
        this.s2 = s2;

        ran = false;
    }

    /**
     * Run the match.
     */
    public void run()
    {
        // These values will be running totals until the end
        s1Avg = 0.0;
        s2Avg = 0.0;
        
        for(int i = 0; i < NUMGAMES; i++)
        {
            s1.reset();
            s2.reset();
            
            for(int j = 0; j < NUMTURNS; j++)
            {
                char choice1 = s1.play();
                char choice2 = s2.play();

                s1.report(choice2);
                s2.report(choice1);

                if(choice1 == 'c' && choice2 == 'c')
                {
                    s1Avg += .5;
                    s2Avg += .5;
                }
                else if(choice1 == 'c' && choice2 == 'd')
                {
                    s1Avg += 10;
                    s2Avg += 0;
                }
                else if(choice1 == 'd' && choice2 == 'c')
                {
                    s1Avg += 0;
                    s2Avg += 10;
                }
                else // choice1 == 'd' && choice2 == 'd'
                {
                    s1Avg += 5;
                    s2Avg += 5;
                }
            }
        }

        s1Avg /= (NUMGAMES * NUMTURNS);
        s2Avg /= (NUMGAMES * NUMTURNS);

        ran = true;
    }

    /**
     * Get the name of the first strategy
     * @return the name
     */
    public String getFirstName()
    {
        return s1.getName();
    }

    /**
     * Get the average time of the first strategy
     * @return a non-negative real value
     * @throws IllegalStateException if this method is called before
     *   the match is run
     */
    public double getFirstAvgTime()
    {
        if(!ran)
            throw new IllegalStateException("do not call before run()");

        return s1Avg;
    }

    /**
     * Get the name of the second strategy
     * @return the name
     */
    public String getSecondName()
    {
        return s2.getName();
    }

    /**
     * Get the average time of the second strategy
     * @return a non-negative real value
     * @throws IllegalStateException if this method is called before
     *   the match is run
     */
    public double getSecondAvgTime()
    {
        if(!ran)
            throw new IllegalStateException("do not call before run()");

        return s2Avg;
    }
}
