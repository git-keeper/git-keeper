public class RegularTriangle extends Polygon {
    private double sideLength;

    public RegularTriangle(double sideLength) {
        super("Regular triangle");
        this.sideLength = sideLength;
    }

    @Override
    public double getArea() {
        return Math.sqrt(3) * (sideLength * sideLength) / 4;
    }
}
