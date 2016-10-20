import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mebjc01
 */
public class ScoreboardTest
{

    @Test
    public void testTwoPlayers()
    {
        Scoreboard s = new Scoreboard();

        s.addName("p1");
        s.addName("p2");

        assertEquals(2, s.getNumPlayers());

        s.addScore("p1", 1, "p2", 2);
        s.addScore("p1", 1, "p1", 1);
        s.addScore("p2", 2, "p2", 2);

        assertEquals(1, s.getScore(1), 0.001);
        assertEquals("p1", s.getName(1));
        assertEquals(2, s.getScore(2), 0.001);
        assertEquals("p2", s.getName(2));

        assertEquals(2, s.getNumPlayers());
    }

    @Test public void testThreePlayers()
    {
        Scoreboard s = new Scoreboard();

        s.addName("p1");
        s.addName("p2");
        s.addName("p3");

        s.addScore("p1", 1, "p2", 2);
        s.addScore("p1", 1, "p3", 3);

        s.addScore("p2", 2, "p3", 3);
        
        s.addScore("p1", 1, "p1", 1);
        s.addScore("p2", 2, "p2", 2);
        s.addScore("p3", 3, "p3", 3);

        assertEquals(1, s.getScore(1), 0.001);
        assertEquals("p1", s.getName(1));
        assertEquals(2, s.getScore(2), 0.001);
        assertEquals("p2", s.getName(2));
        assertEquals(3, s.getScore(3), 0.001);
        assertEquals("p3", s.getName(3));

        assertEquals(3, s.getNumPlayers());
    }

    @Test
    public void testEarlyGet()
    {
        Scoreboard s = new Scoreboard();

        s.addName("p1");
        s.addName("p2");

        // only play 2 games, not 3
        s.addScore("p1", 1, "p2", 2);
        s.addScore("p1", 1, "p1", 1);

        try
        {
            s.getName(1);
            fail("Should thorw State exception");
        }
        catch(IllegalStateException e)
        {
            // good
        }

        try
        {
            s.getScore(1);
            fail("Should thorw State exception");
        }
        catch(IllegalStateException e)
        {
            // good
        }

    }

    @Test
    public void testTooManyAdds()
    {
        Scoreboard s = new Scoreboard();

        s.addName("p1");
        s.addName("p2");

        s.addScore("p1", 1, "p2", 2);
        s.addScore("p1", 1, "p1", 1);
        s.addScore("p2", 2, "p2", 2);

        try
        {
            s.addScore("p1", 1, "p1", 1);
            fail("Should thorw State exception");
        }
        catch(IllegalStateException e)
        {
            // good
        }
    }

    @Test
    public void testBadName()
    {
        Scoreboard s = new Scoreboard();

        s.addName("p1");
        s.addName("p2");

        try
        {
            s.addScore("george", 1, "p2", 2);
            fail("should throw illegal argument");

        }
        catch (IllegalArgumentException e)
        {
            // good
        }

        try
        {
            s.addScore("p2", 2, "george", 1);
            fail("should throw illegal argument");
        }
        catch(IllegalArgumentException e)
        {
            // good
        }
    }

    @Test
    public void testBadIndex()
    {
        Scoreboard s = new Scoreboard();

        s.addName("p1");
        s.addName("p2");

        assertEquals(2, s.getNumPlayers());

        s.addScore("p1", 1, "p2", 2);
        s.addScore("p1", 1, "p1", 1);
        s.addScore("p2", 2, "p2", 2);

        try
        {
            s.getName(0);
            fail("should throw illegal argument");
        }
        catch(IllegalArgumentException e)
        {
            // good
        }

        try
        {
            s.getScore(0);
            fail("should throw illegal argument");
        }
        catch(IllegalArgumentException e)
        {
            // good
        }

        try
        {
            s.getName(4);
            fail("should throw illegal argument");
        }
        catch(IllegalArgumentException e)
        {
            // good
        }

        try
        {
            s.getScore(0);
            fail("should throw illegal argument");
        }
        catch(IllegalArgumentException e)
        {
            // good
        }
    }

    @Test
    public void testDuplicateName()
    {
        Scoreboard s = new Scoreboard();

        s.addName("p1");

        try
        {
            s.addName("p1");
            fail("should throw illegal argument");
        }
        catch(IllegalArgumentException e)
        {
            // good
        }
    }

}