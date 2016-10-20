/**
 * An Entry is the data of the Scoreboard.  It contains the name of
 * a strategy, along with the accumulation of the data from that
 * strategy's matches.
 * 
 * @author mebjc01
 */
public class Entry implements Comparable<Entry>
{
    private String name;
    // The sum of the averages from each of the matches
    private double sum;
    // The number of matches recorded.
    private int count;

    /**
     * Create an entry for the specified strategy name
     * @param name the name of the strategy
     */
    public Entry(String name)
    {
        this.name = name;
        sum = 0.0;
        count = 0;
    }


    /**
     * Record the result for this strategy in a match
     * @param value the average from the match
     */
    public void accumulate(double value)
    {
        sum += value;
        count++;
    }

    /**
     * Get the average from the recorded matches
     * @return a double greater than or equal to 0
     * @throws IllegalStateException if no matches were recorded.
     */
    public double getAverage()
    {
        if(count == 0)
            throw new IllegalStateException("Average called with no data");

        return sum / count;
    }

    /**
     * Get the name in this Entry
     * @return the name
     */
    public String getName()
    {
        return name;
    }

    /**
     * Compare this Entry to another one based on the average of
     * the matches recorded.  Complies with the general contract of
     * compareTo
     * @param that the Entry to compare with
     * @return -1, 0, or 1 for less than, equal to, or greater than.
     */
    public int compareTo(Entry that)
    {
        return Double.compare(this.getAverage(), that.getAverage());
    }

    /**
     * Compare two entries.  By definion, they are equal if the
     * names are equal
     * @param obj the object to compare with
     * @return true of the names are equal, false otherwise.
     */
    @Override
    public boolean equals(Object obj)
    {
        if(!(obj instanceof Entry))
            return false;

        Entry that = (Entry)obj;

        return this.name.equals(that.name);
    }

    /**
     * Compute the hashcode for this Entry
     * @return the hashcode for the name (as this is the
     * value used in equals)
     */
    @Override
    public int hashCode()
    {
        return name.hashCode();
    }
}
