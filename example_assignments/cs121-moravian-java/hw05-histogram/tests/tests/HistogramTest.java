import org.junit.Before;
import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.Assert.*;

public class HistogramTest {
    private final ByteArrayOutputStream outContent = new ByteArrayOutputStream();
    private Histogram hist;

    private String[] getLines() {
        return outContent.toString().split("\\r?\\n");
    }

    @Before
    public void setUp() {
        System.setOut(new PrintStream(outContent));
        hist = new Histogram(10);
    }

    @Test(timeout=1000)
    public void testOneTwo() {
        hist.tally(2);
        hist.prettyPrint();

        String[] outputLines = getLines();

        assertEquals(11, outputLines.length);

        for (int i = 0; i < outputLines.length; i++) {
            if (i == 2)
                assertTrue(outputLines[i].contains("**********"));
            else {
                assertFalse(outputLines[i].contains("*"));
            }
        }
    }

    @Test(timeout=1000)
    public void testOneThreeOneFive() {
        hist.tally(3);
        hist.tally(5);
        hist.prettyPrint();

        String[] outputLines = getLines();

        assertEquals(11, outputLines.length);

        for (int i = 0; i < outputLines.length; i++) {
            if (i == 3 || i == 5)
                assertTrue(outputLines[i].contains("**********"));
            else {
                assertFalse(outputLines[i].contains("*"));
            }
        }
    }

    @Test(timeout=1000)
    public void testThreeSixesOneSevenTwoTens() {
        hist.tally(6);
        hist.tally(6);
        hist.tally(6);
        hist.tally(7);
        hist.tally(10);
        hist.tally(10);
        hist.prettyPrint();

        String[] outputLines = getLines();

        assertEquals(11, outputLines.length);

        for (int i = 0; i < outputLines.length; i++) {
            if (i == 6)
                assertTrue(outputLines[i].contains("**********"));
            else if(i == 7) {
                assertTrue(outputLines[i].contains("***"));
                assertFalse(outputLines[i].contains("****"));
            }
            else if(i == 10) {
                assertTrue(outputLines[i].contains("******"));
                assertFalse(outputLines[i].contains("*******"));
            }
            else {
                assertFalse(outputLines[i].contains("*"));
            }
        }
    }
}