import java.util.ArrayList;

public class Gradebook {
    ArrayList<AssignmentGrade> grades;

    public Gradebook() {
        grades = new ArrayList<>();
    }

    public void addAssignmentGrade(AssignmentGrade assgnGrade) {
        grades.add(assgnGrade);
    }

    public void removeLowestGrade() {
        if (grades.size() == 0)
            return;

        double min = Double.MAX_VALUE;
        int minI = 0;
        int i;
        for (i = 0; i < grades.size(); i++) {
            AssignmentGrade assgnGrade = grades.get(i);
            if (assgnGrade.getGrade() < min) {
                min = assgnGrade.getGrade();
                minI = i;
            }
        }

        grades.remove(minI);
    }

    public int getCount() {
        return grades.size();
    }

    public double getAverage() {
        if (grades.size() == 0)
            return 0.0;

        double sum = 0;
        for (int i = 0; i < grades.size(); i++) {
            AssignmentGrade assgnGrade = grades.get(i);
            sum += assgnGrade.getGrade();
        }

        return sum / grades.size();
    }
}
