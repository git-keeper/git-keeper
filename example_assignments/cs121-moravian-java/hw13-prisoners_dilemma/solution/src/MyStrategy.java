/**
 * Created by julienbombara on 4/3/16.
 */
public class MyStrategy implements Strategy {
    private char prisoner1;
    private char prisoner2;
    private int count1;
    private int count2;

    @Override
    public char play() {
        if(count1 == 0) {
            count1 += 1;
            count2 += 1;
            prisoner2 = 'd';

        }
        else if (count1 == 1) {
            if (prisoner1 == 'c') {
                count1 += 1;
                prisoner2 = 'c'; }
            else if(prisoner1 == 'd'){
                count1 += 1;
                count2 += 1;
                prisoner2 = 'd';
            }
        }
        else if (count1 == 2){
            if(count2==2){
                count1 += 1;
                count2 += 1;
                prisoner2 = 'd';
            }
            else{
                count1 += 1;
                prisoner2 = 'c';
            }
        }
        else if (count1 == 3) {
            if (count2 > 2) {
                count1 += 1;
                prisoner2 = 'd';
            } else {
                count1 += 1;
                prisoner2 = 'c';
            }
        }
        else{
            count1+=1;
            prisoner2 = 'c';
        }
        return prisoner2;
    }

    @Override
    public void report(char opponentChoice) {
        prisoner1 = opponentChoice;

    }

    @Override
    public void reset() {
        count1 = 0;

    }

    @Override
    public String getName() {
        return "Aggressive";
    }
}
