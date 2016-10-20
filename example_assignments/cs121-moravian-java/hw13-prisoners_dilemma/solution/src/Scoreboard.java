import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;

/**
 * The Scoreboard class records the data from each match, and then
 * provides a simple interface to obtain the name and average in
 * rank order.
 *
 * This class ensures that methods are called in the following order.
 * If the user attempts to obtain ranking information before all matches
 * have been recorded, an IllegalStateException will be thrown.
 *
 * 1. call add(String) to add the name of each strategy
 * 2. call addScore(...) with the data for each match.  If there are
 *    n strategies in the competition, then there are n*(n+1)/2
 *    matches.
 * 3. call getName(int) and getAverage(int) as needed to obtain information
 *    about the final ranking.
 * 
 * @author mebjc01
 */
public class Scoreboard
{
    // To quickly access the information for a strategy during
    // data entry, we use a HashMap indexed in the strategy name.
    // Note that the Entry also contains the strategy name.
    private HashMap<String, Entry> entries;

    // After all matches have been recorded, the Entries will be
    // copied to this list and sorted by average low to high.
    private ArrayList<Entry> sortedScores;

    // These fields are used to ensure that all matches are recorded
    // before the rankings are obtained.
    private int numEntriesNeeded;
    private int numEntriesAdded;


    /**
     * Create a new, empty scoreboard.
     */
    public Scoreboard()
    {
        entries = new HashMap<String, Entry>();

        numEntriesNeeded = 0;
        numEntriesAdded = 0;
    }

    /**
     * Add a strategy name to the scoreboard
     * @param name the name to add
     */
    public void addName(String name)
    {
        if(entries.containsKey(name))
            throw new IllegalArgumentException("No duplicates allowed");
        
        entries.put(name, new Entry(name));

        // Compute the new number of matches.
        numEntriesNeeded = entries.size() * (entries.size() + 1) / 2;
    }

    /**
     * Record the results of a specified match
     * @param name1 the name of the first strategy
     * @param score1 the score for the first strategy
     * @param name2 the name of the second strategy
     * @param score2 the score for the second strategy
     * @throws IllegalArgumentException if either strategy name is
     *   not part of the scoreboard
     * @throws IllegalStateException if all matches have already been
     *   recorded
     */
    public void addScore(String name1, double score1, 
            String name2, double score2)
    {
        if(!entries.containsKey(name1))
            throw new IllegalArgumentException("Bad name: " + name1);
        if(!entries.containsKey(name2))
            throw new IllegalArgumentException("Bad name: " + name2);

        if(numEntriesAdded == numEntriesNeeded)
            throw new IllegalStateException("All games played");

        // The above checks ensure that these calls will get valid Entries
        Entry e1 = entries.get(name1);
        Entry e2 = entries.get(name2);

        e1.accumulate(score1);

        // If we are recording the results of a strategy against
        // itself, then we should only record it once.
        if(!name1.equals(name2))
        {
            e2.accumulate(score2);
        }

        numEntriesAdded++;

        // If we have recorded all the maches, it is time to generate
        // the final standings.
        if(numEntriesAdded == numEntriesNeeded)
        {
            sortedScores = new ArrayList<Entry>();

            sortedScores.addAll(entries.values());

            Collections.sort(sortedScores);
        }
    }

    /**
     * Get the name in the specified place
     * @param place the place in question between 1 and the number of
     *   strategies represented
     * @return the name of the strategy in that place
     * @throws IllegalStateException if this method is called before all
     *   matches are recorded
     * @throws IllegalArgumentException if the place is outside the range 1
     *   throw num Stragies (inclusively)
     */
    public String getName(int place)
    {
        if(sortedScores == null)
            throw new IllegalStateException("do not call before all scores added");
        
        if(place < 1 || place > sortedScores.size())
            throw new IllegalArgumentException("bad place: " + place);

        return sortedScores.get(place - 1).getName();
    }

    /**
     * Get the average in the specified place
     * @param place the place in question between 1 and the number of
     *   strategies represented
     * @return the average of the strategy in that place
     * @throws IllegalStateException if this method is called before all
     *   matches are recorded
     * @throws IllegalArgumentException if the place is outside the range 1
     *   throw num Stragies (inclusively)
     */
    public double getScore(int place)
    {
        if(sortedScores == null)
            throw new IllegalStateException("do not call before all scores added");

        if(place < 1 || place > sortedScores.size())
            throw new IllegalArgumentException("bad place: " + place);

        Entry e = sortedScores.get(place - 1);

        return e.getAverage();
    }

    /**
     * Get the number of players recorded
     * @return a non-negative integer.
     */
    public int getNumPlayers()
    {
        return entries.size();
    }
}
