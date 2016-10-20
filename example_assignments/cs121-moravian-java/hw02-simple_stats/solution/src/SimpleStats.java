public class SimpleStats {
    private int count = 0;
    private double sum = 0.0;
    private double min = 0.0;
    private double max = 0.0;

    public void addValue(double newValue) {
        sum += newValue;
        count += 1;

        if (count == 1)
            min = max = newValue;
        else {
            if (newValue < min)
                min = newValue;
            if (newValue > max)
                max = newValue;
        }
    }

    public int getCount() {
        return count;
    }

    public double getMin() {
        return min;
    }

    public double getMax() {
        return max;
    }

    public double getAverage() {
        if (count == 0) {
            return 0;
        }
        else {
            return sum / count;
        }
    }
}
