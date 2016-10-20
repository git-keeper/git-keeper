import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

public class SimpleStatsTest {
    private SimpleStats ss;

    @Before
    public void setUp() {
        ss = new SimpleStats();
    }

    @Test
    public void testEmpty() {
        assertEquals(0, ss.getCount());
        assertEquals(0.0, ss.getMin(), 0.001);
        assertEquals(0.0, ss.getMax(), 0.001);
        assertEquals(0.0, ss.getAverage(), 0.001);
    }

    @Test
    public void testOne() {
        ss.addValue(1.0);

        assertEquals(1, ss.getCount());
        assertEquals(1.0, ss.getMin(), 0.001);
        assertEquals(1.0, ss.getMax(), 0.001);
        assertEquals(1.0, ss.getAverage(), 0.001);
    }

    @Test
    public void testThree() {
        ss.addValue(100.0);
        ss.addValue(150.0);
        ss.addValue(200.0);

        assertEquals(3, ss.getCount());
        assertEquals(100.0, ss.getMin(), 0.001);
        assertEquals(200.0, ss.getMax(), 0.001);
        assertEquals(150.0, ss.getAverage(), 0.001);
    }
}
