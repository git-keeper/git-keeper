/**
 * Created by laurenmateo on 4/3/16.
 */
public class WhatIsAStrategy implements Strategy
{
    private int count=0;
    public char play()
    {
        count++;
        if(count<6)
            return 'c';
        else
            return 'd';
    }
    public void report(char opponentChoice)
    {

    }
    public void reset()
    {

    }
    public String getName()
    {
        return "WhatIsAStrategy";
    }
}
