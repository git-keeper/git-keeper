import java.util.ArrayList;

/**
 * Created by nws on 4/4/16.
 */
public abstract class StrategiesFactory {
    protected ArrayList<Strategy> strategies = new ArrayList<>();

    public ArrayList<Strategy> getStrategies() {
        return strategies;
    }
}
