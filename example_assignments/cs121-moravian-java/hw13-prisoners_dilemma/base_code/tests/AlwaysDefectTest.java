import org.junit.Test;

import static org.junit.Assert.*;

/**
 * @author mebjc01
 */
public class AlwaysDefectTest {
    @Test
    public void testNew() {
        AlwaysDefect t = new AlwaysDefect();

        assertEquals('d', t.play());
    }

    @Test
    public void testResponse() {
        AlwaysDefect t = new AlwaysDefect();

        assertEquals('d', t.play());
        t.report('d');
        assertEquals('d', t.play());
        t.report('c');
        assertEquals('d', t.play());
    }

    @Test
    public void testReset() {
        AlwaysDefect t = new AlwaysDefect();

        t.report('d');
        assertEquals('d', t.play());
        t.reset();
        assertEquals('d', t.play());
    }

    @Test
    public void testGetName() {
        AlwaysDefect t = new AlwaysDefect();

        assertEquals("AlwaysDefect", t.getName());
    }

}