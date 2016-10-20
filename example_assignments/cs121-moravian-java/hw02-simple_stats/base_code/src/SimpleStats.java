public class SimpleStats {
    private int count = 0;
    private double sum = 0.0;

    public void addValue(double newValue) {
        sum += newValue;
        count += 1;
    }

    public int getCount() {
        return count;
    }

    public double getAverage() {
        if (count == 0) {
            return 0.0;
        }
        else {
            return sum / count;
        }
    }
}
