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

    public void prettyPrint() {
        int maxCount = 0;

        for (int i = 0; i < counts.length; i++) {
            if (counts[i] > maxCount)
                maxCount = counts[i];
        }

        for (int i = 0; i < counts.length; i++) {
            System.out.print(i + ": ");

            int starCount = (int)(((double)counts[i] / maxCount) * 10);
            for (int starNum = 0; starNum < starCount; starNum++)
                System.out.print('*');
            System.out.println();
        }
    }
}
