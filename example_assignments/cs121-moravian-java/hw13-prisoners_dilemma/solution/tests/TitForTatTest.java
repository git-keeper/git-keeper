import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mebjc01
 */
public class TitForTatTest
{

    @Test
    public void testNew()
    {
        TitForTat t = new TitForTat();

        assertEquals('c', t.play());
    }

    @Test public void testResponse()
    {
        TitForTat t = new TitForTat();

        assertEquals('c', t.play());
        t.report('d');
        assertEquals('d', t.play());
        t.report('c');
        assertEquals('c', t.play());
    }

    @Test
    public void testReset()
    {
        TitForTat t = new TitForTat();

        t.report('d');
        assertEquals('d', t.play());
        t.reset();
        assertEquals('c', t.play());
    }

    @Test
    public void testGetName()
    {
        TitForTat t = new TitForTat();

        assertEquals("TitForTat", t.getName());
    }

}