import org.junit.Test;

import static org.junit.Assert.*;

public class RightTriangleTest {
    @Test
    public void testRightTriangle() {
        Polygon rt1 = new RightTriangle(3.0, 4.0);
        assertEquals("A right triangle with legs of lengths 3.0 and 4.0 should have an area of 6.0", 6.0, rt1.getArea(), 0.001);

        Polygon rt2 = new RightTriangle(10.0, 20.0);
        assertEquals("A right triangle with legs of lengths 10.0 and 20.0 should have an area of 100.0", 100.0, rt2.getArea(), 0.001);

        assertEquals("The description of a RightTriangle should be \"Right triangle\"", "Right triangle", rt2.getDescription());
    }
}