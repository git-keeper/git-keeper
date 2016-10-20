import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        ArrayList<Polygon> polygons = new ArrayList<>();

        polygons.add(new Square(5.0));
        polygons.add(new RegularTriangle(5.0));

        for (Polygon p : polygons)
            System.out.println(p);
    }
}
