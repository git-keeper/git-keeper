import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mebjc01
 */
public class ColemanTest
{

    @Test
    public void testNew()
    {
        Coleman t = new Coleman();

        assertEquals('c', t.play());
    }

    @Test public void testResponse()
    {
        Coleman t = new Coleman();

        assertEquals('c', t.play());
        t.report('d');
        assertEquals('d', t.play());
        t.report('c');
        assertEquals('c', t.play());
    }

    @Test
    public void testReset()
    {
        Coleman t = new Coleman();

        t.report('d');
        assertEquals('d', t.play());
        t.reset();
        assertEquals('c', t.play());
    }

    @Test
    public void testGetName()
    {
        Coleman t = new Coleman();

        assertEquals("Coleman", t.getName());
    }
}