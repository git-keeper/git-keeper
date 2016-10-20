public class SimpleStatsTestDrive {
    public static void main(String[] args) {
        SimpleStats ss = new SimpleStats();

        System.out.println(ss.getCount());
        System.out.println(ss.getMin());
        System.out.println(ss.getMax());
        System.out.println(ss.getAverage());

        ss.addValue(1.0);

        System.out.println(ss.getCount());
        System.out.println(ss.getMin());
        System.out.println(ss.getMax());
        System.out.println(ss.getAverage());

        ss.addValue(2.0);

        System.out.println(ss.getCount());
        System.out.println(ss.getMin());
        System.out.println(ss.getMax());
        System.out.println(ss.getAverage());

        ss.addValue(100.0);

        System.out.println(ss.getCount());
        System.out.println(ss.getMin());
        System.out.println(ss.getMax());
        System.out.println(ss.getAverage());
    }
}
