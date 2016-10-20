import java.util.ArrayList;

public class StatsList extends ArrayList<Double> {
    public double min() {
        if (size() == 0)
            return 0.0;

        double min = Double.MAX_VALUE;

        for (double n : this) {
            if (n < min)
                min = n;
        }

        return min;
    }

    public double max() {
        if (size() == 0)
           return 0.0;

        double max = -1 * Double.MAX_VALUE;

        for (double n : this) {
            if (n > max)
                max = n;
        }

        return max;
    }

    public double sum() {
        double sum = 0.0;

        for (double n : this)
            sum += n;

        return sum;
    }

    public double average() {
        if (size() == 0) {
            return 0.0;
        }
        else {
            return sum() / size();
        }
    }
}
