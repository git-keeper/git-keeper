/** Runs like the tit-for-tat method.
 *
 * @author Chris Kieszek
 */
public class K1 implements Strategy
{

    private String name;
    private int game;
    
    public K1()
    {
        name = "K1";
        game = 1;
    }
    public char play()
    {
        if(game % 2 == 0)
        {
            return 'd';
        }
        else
        {
            return 'c';
        }
    }

    public void report(char opponentChoice)
    {
        return;
    }

    public void reset()
    {
       game = 1; 
    }

    public String getName()
    {
        return name = "K1";
    }

}
