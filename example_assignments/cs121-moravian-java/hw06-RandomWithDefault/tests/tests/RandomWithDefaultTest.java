import org.junit.Test;

import static org.junit.Assert.*;

public class RandomWithDefaultTest {
    @Test(timeout=1000)
    public void testTwentyValues() {
        RandomWithDefault rwd = new RandomWithDefault(30.0, 40.0, 50.0, 20);

        for(int i = 0; i < 20; i++) {
            assertTrue(30.0 <= rwd.getValue(i));
            assertTrue(40.0 > rwd.getValue(i));
        }

        assertEquals(50.0, rwd.getValue(-1), 0.001);
        assertEquals(50.0, rwd.getValue(-2), 0.001);
        assertEquals(50.0, rwd.getValue(20), 0.001);
        assertEquals(50.0, rwd.getValue(21), 0.001);
    }
}
