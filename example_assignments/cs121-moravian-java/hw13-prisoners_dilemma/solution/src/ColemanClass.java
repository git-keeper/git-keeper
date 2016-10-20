/**
 * Created by nws on 4/4/16.
 */
public class ColemanClass extends StrategiesFactory {
    public ColemanClass() {
        strategies.add(new Coleman());
        strategies.add(new ChuckNorrisStrat());
        strategies.add(new DoumithTitForTatWithForgiveness());
        strategies.add(new DoumithTitForTwoTats());
        strategies.add(new DoumithUnforgiving());
        strategies.add(new EmmittStrategy());
        strategies.add(new FiveGirlsPregnentAndCounting());
        strategies.add(new ItsObama());
        strategies.add(new K1());
        strategies.add(new K2());
        strategies.add(new K3());
        strategies.add(new NickStratFirstSemester());
        strategies.add(new RomoStrategy());
        strategies.add(new T1());
        strategies.add(new T2());
        strategies.add(new T3());
        strategies.add(new TerrellStrategy());
    }
}
