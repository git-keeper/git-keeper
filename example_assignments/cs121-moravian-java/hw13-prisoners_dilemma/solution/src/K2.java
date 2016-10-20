/** This strategy cooperates first and then depending on the # of games,
 * it will either cooperate or defect.
 * @author Chris Kieszek
 */
public class K2 implements Strategy
{

    private String name;
    private char myChoice;
    private int game;
    
    public K2()
    {
        name = "K2";
        myChoice = 'c';
        game = 1;
    }
    
    public char play()
    {
       return myChoice; 
    }

    public void report(char opponentChoice)
    {
        if(game % 2 == 0)
        {
            myChoice = opponentChoice;
        }
        else
        {
            myChoice = 'c';
        }
        game ++;
        
    }

    public void reset()
    {
        game = 1;
        myChoice = 'c';
    }

    public String getName()
    {
        return name;
    }

}
