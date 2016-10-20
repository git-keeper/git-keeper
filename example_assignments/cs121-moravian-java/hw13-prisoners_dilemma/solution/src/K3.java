/** This strategy takes random numbers for 1 to 6
 *  and then depending on the value, will either cooperate or defect.
 * @author Chris Kieszek
 */
public class K3 implements Strategy
{

    private String name;
    private int num;
    
    public K3()
    {
        name = "K3";
    }
    public char play()
    {
        num = (int)(Math.random() * 6 + 1);
        if(num == 1)
            return 'c';
        else
            return 'd';       
    }

    public void report(char opponentChoice)
    {
        return;
        
    }

    public void reset()
    {
        return;
    }

    public String getName()
    {
        return name;
    }

}
