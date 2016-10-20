/**
 * Created by nws on 4/4/16.
 */
public class BasicStrategies extends StrategiesFactory {
    public BasicStrategies() {
        strategies.add(new AlwaysCooperate());
        strategies.add(new AlwaysDefect());
        strategies.add(new TitForTat());
    }
}
