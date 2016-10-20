public class HistogramTestDrive {
    public static void main(String[] args) {
        Histogram hist = new Histogram(10);

        hist.tally(6);
        hist.tally(6);
        hist.tally(6);
        hist.tally(7);
        hist.tally(10);
        hist.tally(10);

        hist.prettyPrint();
    }
}
