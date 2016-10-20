import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mebjc01
 */
public class AlwaysCooperateTest
{
    @Test
    public void testNew()
    {
        AlwaysCooperate t = new AlwaysCooperate();

        assertEquals('c', t.play());
    }

    @Test public void testResponse()
    {
        AlwaysCooperate t = new AlwaysCooperate();

        assertEquals('c', t.play());
        t.report('d');
        assertEquals('c', t.play());
        t.report('c');
        assertEquals('c', t.play());
    }

    @Test
    public void testReset()
    {
        AlwaysCooperate t = new AlwaysCooperate();

        t.report('d');
        assertEquals('c', t.play());
        t.reset();
        assertEquals('c', t.play());
    }

    @Test
    public void testGetName()
    {
        AlwaysCooperate t = new AlwaysCooperate();

        assertEquals("AlwaysCooperate", t.getName());
    }


}