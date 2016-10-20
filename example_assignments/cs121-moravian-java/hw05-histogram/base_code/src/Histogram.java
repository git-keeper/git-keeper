public class Histogram {
    private int[] counts;

    public Histogram(int maxNumber) {
        counts = new int[maxNumber + 1];
    }

    public void tally(int number) {
        counts[number] += 1;
    }

    public int getCount(int number) {
        return counts[number];
    }

    // Implement the prettyPrint() method here
}
