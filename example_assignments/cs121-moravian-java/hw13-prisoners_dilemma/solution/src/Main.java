import java.util.ArrayList;

/**
 * It's main.  It does all the magic.
 * @author mebjc01
 */
public class Main
{
    public static void main(String[] args)
    {
        ArrayList<StrategiesFactory> factories = new ArrayList<>();

        factories.add(new BasicStrategies());
        factories.add(new Spring2016A());
        factories.add(new Spring2016B());
        factories.add(new ColemanClass());

        Competition c = new Competition();

        for (StrategiesFactory f : factories)
        {
            for (Strategy s : f.getStrategies())
            {
                c.add(s);
            }
        }

        c.run();

        for(int i = 1; i <= c.getNumStrategies(); i++)
        {
            System.out.println(c.getName(i) + " " + c.getAverageTime(i));
        }
    }
}
