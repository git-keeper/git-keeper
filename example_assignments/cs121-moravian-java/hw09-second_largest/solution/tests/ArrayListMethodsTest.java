import org.junit.Test;

import java.util.ArrayList;

import static org.junit.Assert.*;

public class ArrayListMethodsTest {
    /**
     * Make sure maxElement() returns Integer.MIN_VALUE for an empty list
     */
    @Test
    public void testMaxEmpty() {
        // create an empty list
        ArrayList<Integer> ints = new ArrayList<>();

        // Should return Integer.MIN_VALUE for an empty list
        assertEquals(Integer.MIN_VALUE, ArrayListMethods.maxElement(ints));
    }

    /**
     * Make sure maxElement() returns the proper value when the
     * max is the first element of the list
     */
    @Test
    public void testMaxFirst() {
        // create an empty list
        ArrayList<Integer> ints = new ArrayList<>();

        // add 3 values with the max at the beginning
        ints.add(3);
        ints.add(2);
        ints.add(1);

        // maxElement() should return 3
        assertEquals(3, ArrayListMethods.maxElement(ints));
    }

    /**
     * Make sure maxElement() returns the proper value when the
     * max is the last element of the list
     */
    @Test
    public void testMaxLast() {
        // create an empty list
        ArrayList<Integer> ints = new ArrayList<>();

        // add 3 values with the max at the end. also tests
        // negatives
        ints.add(-2);
        ints.add(-3);
        ints.add(-1);

        // maxElement() should return -1
        assertEquals(-1, ArrayListMethods.maxElement(ints));
    }

    @Test
    public void testSecondEmpty() {
        ArrayList<Integer> ints = new ArrayList<>();

        assertEquals(Integer.MIN_VALUE, ArrayListMethods.secondLargest(ints));
    }

    @Test
    public void testSecondOne() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(1);

        assertEquals(Integer.MIN_VALUE, ArrayListMethods.secondLargest(ints));
    }

    @Test
    public void testSecondFirst() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(2);
        ints.add(3);
        ints.add(1);

        assertEquals(2, ArrayListMethods.secondLargest(ints));
    }

    @Test
    public void testSecondMiddle() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(-1);
        ints.add(-2);
        ints.add(-3);

        assertEquals(-2, ArrayListMethods.secondLargest(ints));
    }

    @Test
    public void testSecondLast() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(-10);
        ints.add(20);
        ints.add(3);

        assertEquals(3, ArrayListMethods.secondLargest(ints));
    }

    @Test
    public void testMaxRepeat() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(1);
        ints.add(10);
        ints.add(5);
        ints.add(10);

        assertEquals(5, ArrayListMethods.secondLargest(ints));
    }

    @Test
    public void testSecondRepeat() {
        ArrayList<Integer> ints = new ArrayList<>();

        ints.add(5);
        ints.add(10);
        ints.add(5);
        ints.add(1);

        assertEquals(5, ArrayListMethods.secondLargest(ints));
    }
}
