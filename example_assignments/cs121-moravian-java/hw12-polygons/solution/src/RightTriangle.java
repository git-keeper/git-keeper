public class RightTriangle extends Polygon {
    private double leg1Length;
    private double leg2Length;

    public RightTriangle(double leg1Length, double leg2Length) {
        super("Right triangle");
        this.leg1Length = leg1Length;
        this.leg2Length = leg2Length;
    }

    @Override
    public double getArea() {
        return leg1Length * leg2Length / 2;
    }
}
