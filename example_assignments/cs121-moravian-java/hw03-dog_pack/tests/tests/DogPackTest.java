import org.junit.Before;
import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.Assert.*;

public class DogPackTest {
    private final ByteArrayOutputStream outContent = new ByteArrayOutputStream();

    @Before
    public void setUp() {
        System.setOut(new PrintStream(outContent));
    }

    @Test
    public void testOne() {
        String[] names = {"Bob"};
        DogPack pack = new DogPack(names);
        pack.makeRuckus();

        String[] outputLines = outContent.toString().split("\\r?\\n");

        assertEquals(1, outputLines.length);
        assertTrue(outputLines[0].contains("Bob"));
    }

    @Test
    public void testFour() {
        String[] names = {"Lucy", "Lauren", "Lynda", "Lydia"};
        DogPack pack = new DogPack(names);
        pack.makeRuckus();

        String[] outputLines = outContent.toString().split("\\r?\\n");

        assertEquals(4, outputLines.length);
        for (int i = 0; i < names.length; i++) {
            assertTrue(outputLines[i].contains(names[i]));
        }
    }
}
