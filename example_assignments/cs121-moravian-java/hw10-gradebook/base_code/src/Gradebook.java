import java.util.ArrayList;

public class Gradebook {
    ArrayList<AssignmentGrade> grades;

    public Gradebook() {
        grades = new ArrayList<>();
    }

    public void addAssignmentGrade(AssignmentGrade assgnGrade) {
        grades.add(assgnGrade);
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
