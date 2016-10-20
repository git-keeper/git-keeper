import org.junit.Test;

import static org.junit.Assert.*;

public class GradebookTest {
    @Test(timeout=1000)
    public void testEmptyBook() {
        Gradebook book = new Gradebook();

        assertEquals(0, book.getCount());
        assertEquals(0.0, book.getAverage(), 0.001);
    }

    @Test(timeout=1000)
    public void testOneGrade() {
        Gradebook book = new Gradebook();

        book.addAssignmentGrade(new AssignmentGrade("Homework 1", 88.0));

        assertEquals(1, book.getCount());
        assertEquals(88.0, book.getAverage(), 0.001);
    }

    @Test(timeout=1000)
    public void testTwoGrades() {
        Gradebook book = new Gradebook();

        book.addAssignmentGrade(new AssignmentGrade("Homework 1", 88.0));
        book.addAssignmentGrade(new AssignmentGrade("Homework 2", 84.0));

        assertEquals(2, book.getCount());
        assertEquals(86.0, book.getAverage(), 0.001);
    }
}
