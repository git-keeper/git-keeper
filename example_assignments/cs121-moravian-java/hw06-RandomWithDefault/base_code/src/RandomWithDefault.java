public class RandomWithDefault {
    private double[] values;
    private double defaultValue;

    public RandomWithDefault(double min, double max, double theDefault, int count) {
        values = new double[count];

        if (max < min) {
            double temp = min;
            min = max;
            max = temp;
        }

        double width = max - min;

        for (int i = 0; i < count; i++) {
            double randVal = Math.random() * width + min;
            values[i] = randVal;
        }

        defaultValue = theDefault;
    }

    public double getValue(int index) {
        if (index > values.length || index < 0)
            return defaultValue;
        else
            return values[index];
    }
}
