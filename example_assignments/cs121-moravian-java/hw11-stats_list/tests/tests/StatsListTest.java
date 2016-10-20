import org.junit.Before;
import org.junit.Test;

import java.util.ArrayList;

import static org.junit.Assert.*;

public class StatsListTest {
    private StatsList ss;

    @Before
    public void setUp() {
        ss = new StatsList();
    }

    @Test(timeout=1000)
    public void testEmpty() {
        assertTrue(ss instanceof ArrayList);

        assertEquals("Expected size() to be 0 for an empty list.", 0,
                ss.size());
        assertEquals("Expected min() to be 0.0 for an empty list.", 0.0,
                ss.min(), 0.001);
        assertEquals("Expected max() to be 0.0 for an empty list.", 0.0,
                ss.max(), 0.001);
        assertEquals("Expected average() to be 0.0 for an emtpy list.", 0.0,
                ss.average(), 0.001);
        assertEquals("Expected sum() to be 0.0 for an emtpy list.", 0.0,
                ss.sum(), 0.001);
    }

    @Test(timeout=1000)
    public void testOne() {
        ss.add(1.0);

        assertEquals("Expected size() to be 1 for this list: " + ss.toString(),
                1, ss.size());
        assertEquals("Expected min() to be 1.0 for this list: " + ss.toString(),
                1.0, ss.min(), 0.001);
        assertEquals("Expected max() to be 1.0 for this list: " + ss.toString(),
                1.0, ss.max(), 0.001);
        assertEquals("Expected average() to be 1.0 for this list: " + ss.toString(),
                1.0, ss.average(), 0.001);
        assertEquals("Expected sum() to be 1.0 for this list: " + ss.toString(),
                1.0, ss.sum(), 0.001);
    }

    @Test(timeout=1000)
    public void testThree() {
        ss.add(100.0);
        ss.add(150.0);
        ss.add(200.0);

        assertEquals("Expected size() to be 3 for this list: " + ss.toString(),
                3, ss.size());
        assertEquals("Expected min() to be 100.0 for this list: " + ss.toString(),
                100.0, ss.min(), 0.001);
        assertEquals("Expected max() to be 200.0 for this list: " + ss.toString(),
                200.0, ss.max(), 0.001);
        assertEquals("Expected average() to be 150.0 for this list: " + ss.toString(),
                150.0, ss.average(), 0.001);
        assertEquals("Expected sum() to be 450.0 for this list: " + ss.toString(),
                450.0, ss.sum(), 0.001);
    }

    @Test(timeout=1000)
    public void testNegatives() {
        ss.add(-100.0);
        ss.add(-120.0);
        ss.add(-80.0);

        assertEquals("Expected size() to be 3 for this list: " + ss.toString(),
                3, ss.size());
        assertEquals("Expected min() to be -120.0 for this list: " + ss.toString(),
                -120.0, ss.min(), 0.001);
        assertEquals("Expected max() to be -80.0 for this list: " + ss.toString(),
                -80.0, ss.max(), 0.001);
        assertEquals("Expected average() to be -100.0 for this list: " + ss.toString(),
                -100.0, ss.average(), 0.001);
        assertEquals("Expected sum() to be -300.0 for this list: " + ss.toString(),
                -300.0, ss.sum(), 0.001);
    }
}
