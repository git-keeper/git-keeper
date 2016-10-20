import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mebjc01
 */
public class CompetitionTest
{

    @Test
    public void testTwoPlayers()
    {
        Competition c = new Competition();

        c.add(new AlwaysCooperate());
        c.add(new AlwaysDefect());

        c.run();


        //AC vs. AC = 0.5
        //AC vs. AD = 10.0 and 0.0
        //AD vs. AD = 5
        // Avg AC = (.5 + 10) / 2 = 5.25
        // Avg AD = (5 + 0) / 2 = 2.5
        assertEquals(2.5, c.getAverageTime(1), 0.001);
        assertEquals("AlwaysDefect", c.getName(1));
        assertEquals(5.25, c.getAverageTime(2), 0.001);
        assertEquals("AlwaysCooperate", c.getName(2));

        assertEquals(2, c.getNumStrategies());
    }

    @Test
    public void testTwoPlayers2()
    {
        Competition c = new Competition();

        c.add(new AlwaysCooperate());
        c.add(new TitForTat());

        c.run();

        // Both will cooperate at each step
        // Hard to say which go first on a tie...
        assertEquals(.5, c.getAverageTime(1), 0.001);
        assertEquals(.5, c.getAverageTime(2), 0.001);
    }

    @Test
    public void testNullStrategy()
    {
        Competition c = new Competition();

        try
        {
            c.add(null);
            fail("IllegalARgumentException should be thrown");
        }
        catch(IllegalArgumentException e)
        {
            // do nothing, we should be here
        }
    }
}