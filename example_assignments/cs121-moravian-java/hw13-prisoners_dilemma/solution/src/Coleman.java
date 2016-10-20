/**
 * The fancy Coleman strategy.  No, I'm not going to tell
 * you how it works.  You figure out your own strategies!
 * 
 * @author mebjc01
 */
public class Coleman implements Strategy
{
    int numCoops;
    int numDefs;

    public Coleman()
    {
        numCoops = 0;
        numDefs = 0;
    }

    public char play()
    {
        if(numCoops >= numDefs)
            return 'c';

        return 'd';
    }

    public void report(char opponentChoice)
    {
        if(opponentChoice == 'c')
            numCoops++;
        else
            numDefs++;
    }

    public void reset()
    {
        numCoops = 0;
        numDefs = 0;
    }

    public String getName()
    {
        return "Coleman";
    }

}
