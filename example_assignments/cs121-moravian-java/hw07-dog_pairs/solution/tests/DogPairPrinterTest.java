import org.junit.Before;
import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.Assert.*;

public class DogPairPrinterTest {
    private final ByteArrayOutputStream outContent = new ByteArrayOutputStream();

    @Before
    public void setUp() {
        System.setOut(new PrintStream(outContent));
    }

    @Test
    public void testThree() {
        Dog[] dogs = {new Dog("Sam"), new Dog("Sue"), new Dog("Sharon")};
        DogPairPrinter.printDogPairs(dogs);

        String[] outputLines = outContent.toString().split("\\r?\\n");

        assertEquals(3, outputLines.length);
        assertTrue(outputLines[0].contains("Sam and Sue"));
        assertTrue(outputLines[1].contains("Sam and Sharon"));
        assertTrue(outputLines[2].contains("Sue and Sharon"));
    }

    @Test
    public void testFour() {
        Dog[] dogs = {new Dog("Sam"), new Dog("Sue"), new Dog("Sharon"), new Dog("Steve")};
        DogPairPrinter.printDogPairs(dogs);

        String[] outputLines = outContent.toString().split("\\r?\\n");

        assertEquals(6, outputLines.length);
        assertTrue(outputLines[0].contains("Sam and Sue"));
        assertTrue(outputLines[1].contains("Sam and Sharon"));
        assertTrue(outputLines[2].contains("Sam and Steve"));
        assertTrue(outputLines[3].contains("Sue and Sharon"));
        assertTrue(outputLines[4].contains("Sue and Steve"));
        assertTrue(outputLines[5].contains("Sharon and Steve"));
    }
}