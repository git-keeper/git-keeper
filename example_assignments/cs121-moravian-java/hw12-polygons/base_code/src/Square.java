public class Square extends Polygon {
    private double sideLength;

    public Square(double sideLength) {
        super("Square");
        this.sideLength = sideLength;
    }

    @Override
    public double getArea() {
        return sideLength * sideLength;
    }
}
