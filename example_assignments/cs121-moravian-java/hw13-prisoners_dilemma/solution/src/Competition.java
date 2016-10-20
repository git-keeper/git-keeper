import java.util.ArrayList;

/**
 * This class acts as the coordinator for a competition between
 * strategies.
 * 
 * @author mebjc01
 */
public class Competition
{
    ArrayList<Strategy> strategies;
    Scoreboard scores;

    /**
     * Create a new competition with no strategies.
     */
    public Competition()
    {
        strategies = new ArrayList<Strategy>();
        scores = new Scoreboard();
    }

    /**
     * Add a strategy to the competition
     * @param s the strategy to add
     * @throws IllegalArgumentException if s is null
     */
    public void add(Strategy s)
    {
        if(s == null)
            throw new IllegalArgumentException("null Strategy not allowed");
        
        strategies.add(s);
        scores.addName(s.getName());
    }

    /**
     * Run the competition with the current strategies.
     */
    public void run()
    {
        for(int i = 0; i < strategies.size(); i++)
        {
            for(int j = i; j < strategies.size(); j++)
            {
                Match m = new Match(strategies.get(i), strategies.get(j));

                m.run();

                scores.addScore(m.getFirstName(), m.getFirstAvgTime(), 
                        m.getSecondName(), m.getSecondAvgTime());
            }
        }
    }

    /**
     * Get the the name of the strategy in the specified place
     * @param place a value between 1 and the number of strategies (inclusive)
     * @return the name of a corresponding strategy
     * @throws IllegalArgumentException if place is outside the specified range
     */
    public String getName(int place)
    {
        if(place < 1 || place > strategies.size())
            throw new IllegalArgumentException("Bad place: " + place);

        return scores.getName(place);
    }

    /**
     * Get the average time of the strategy in the specifed place
     * @param place a value between 1 and the number of strategies (inclusive)
     * @return the average time of the corresponding strategy
     * @throws IllegalArgumentExcpetion if place is outside the specifed range
     */
    public double getAverageTime(int place)
    {
        if(place < 1 || place > strategies.size())
            throw new IllegalArgumentException("Bad place: " + place);

        return scores.getScore(place);
    }

    /**
     * Get the number of strategies in the competition
     * @return a non-negative integer
     */
    public int getNumStrategies()
    {
        return strategies.size();
    }
}
