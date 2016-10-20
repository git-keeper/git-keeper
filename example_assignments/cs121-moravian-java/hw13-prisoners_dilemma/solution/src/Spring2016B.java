/**
 * Created by nws on 4/4/16.
 */
public class Spring2016B extends StrategiesFactory {
    public Spring2016B() {
        strategies.add(new PlayingNicely());
        strategies.add(new MattDill_SimpleMajority());
        strategies.add(new newStrategy());
        strategies.add(new OppositeOfOpponent());
        strategies.add(new ComboBreaker());
        strategies.add(new TitForTatMeetsRandom());
        strategies.add(new CooperateThenCopycat());
        strategies.add(new AlwaysChange());
        strategies.add(new KyleThoman());
        strategies.add(new Opposite());
        strategies.add(new DoWhatItDo());
    }
}
