import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mebjc01
 */
public class MatchTest
{

    @Test
    public void testDoubleAlwaysCoop()
    {
        Match m = new Match(new AlwaysCooperate(), new AlwaysCooperate());

        m.run();

        assertEquals(.5, m.getFirstAvgTime(), 0.001);
        assertEquals(.5, m.getSecondAvgTime(), 0.001);
    }

    @Test
    public void testDoubleAlwaysDefect()
    {
        Match m = new Match(new AlwaysDefect(), new AlwaysDefect());

        m.run();

        assertEquals(5, m.getFirstAvgTime(), 0.001);
        assertEquals(5, m.getSecondAvgTime(), 0.001);
    }

    @Test
    public void testOpposites()
    {
        Match m = new Match(new AlwaysDefect(), new AlwaysCooperate());

        m.run();

        assertEquals(0, m.getFirstAvgTime(), 0.001);
        assertEquals(10, m.getSecondAvgTime(), 0.001);
    }

    @Test
    public void testTimingError()
    {
        Match m = new Match(new AlwaysDefect(), new AlwaysDefect());

        try
        {
            m.getFirstAvgTime();
            fail("Should throw IllegalState");
        }
        catch (IllegalStateException e)
        {
            // good!
        }
    }

    @Test
    public void testBadParams()
    {
        try
        {
            Match m = new Match(null, new AlwaysDefect());
            fail("Should throw IllegalArgument");
        }
        catch (IllegalArgumentException e)
        {
            // good!
        }

        try
        {
            Match m = new Match(new AlwaysDefect(), null);
            fail("Should throw IllegalArgument");
        }
        catch (IllegalArgumentException e)
        {
            // good!
        }

    }
}