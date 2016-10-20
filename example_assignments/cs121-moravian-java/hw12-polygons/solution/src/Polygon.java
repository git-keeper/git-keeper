public abstract class Polygon {
    private String description;

    public Polygon(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    @Override
    public String toString() {
        return description + " whose area is " + getArea();
    }

    public abstract double getArea();
}
