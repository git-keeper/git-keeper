import java.util.Random;

/**
 * Created by manahax on 4/3/16.
 */
public class Luckyboy implements Strategy{
    Random ran=new Random(1);
    int RandNum=ran.nextInt(1);

    public char play() {


        if(RandNum==1){
            return 'd';
        }

        return 'c';
    }


    public void report(char opponentChoice) {

    }


    public void reset() {
        RandNum=0;
    }


    public String getName() {
        return "Lucky boy";
    }
}
