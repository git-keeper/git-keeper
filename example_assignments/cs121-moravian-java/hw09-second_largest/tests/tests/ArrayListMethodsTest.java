import org.junit.Test;

import java.util.ArrayList;

import static org.junit.Assert.*;

public class ArrayListMethodsTest {
    @Test(timeout=1000)
    public void testSecondEmpty() {
        ArrayList<Integer> ints = new ArrayList<>();

        assertEquals(Integer.MIN_VALUE, ArrayListMethods.secondLargest(ints));
    }

    @Test(timeout=1000)
    public void testSecondOne() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(1);

        assertEquals(Integer.MIN_VALUE, ArrayListMethods.secondLargest(ints));
    }

    @Test(timeout=1000)
    public void testSecondFirst() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(2);
        ints.add(3);
        ints.add(1);

        assertEquals(2, ArrayListMethods.secondLargest(ints));
    }

    @Test(timeout=1000)
    public void testSecondMiddle() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(-1);
        ints.add(-2);
        ints.add(-3);

        assertEquals(-2, ArrayListMethods.secondLargest(ints));
    }

    @Test(timeout=1000)
    public void testSecondLast() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(-10);
        ints.add(20);
        ints.add(3);

        assertEquals(3, ArrayListMethods.secondLargest(ints));
    }

    @Test(timeout=1000)
    public void testMaxRepeat() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(1);
        ints.add(10);
        ints.add(5);
        ints.add(10);

        assertEquals(5, ArrayListMethods.secondLargest(ints));
    }

    @Test(timeout=1000)
    public void testSecondRepeat() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(5);
        ints.add(10);
        ints.add(5);
        ints.add(1);

        assertEquals(5, ArrayListMethods.secondLargest(ints));
    }
}
