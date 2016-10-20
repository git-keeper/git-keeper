
public class SHStrategy implements Strategy {
    private int dcount;
    private int ccount;
    private char opponentLastPlay;

    public SHStrategy() {
        reset();
    }

    //@Override
    public char play() {
        char p;
        if (Math.abs(dcount-ccount)<=2){
            p='d';
        }
        else {
            if (dcount>ccount){
                if (opponentLastPlay=='d'){
                    p='d';
                }
                else p='c';
            }
            else{
                if (opponentLastPlay=='c'){
                    p='d';
                }
                else p='c';
            }
        }

        return p;
    }

    //@Override
    public void report(char opponentChoice) {
        opponentLastPlay = opponentChoice;
        if (opponentLastPlay=='d'){
            dcount+=1;
        }
        else ccount+=1;
    }

    //@Override
    public void reset() {
        dcount=0;
        ccount=0;
    }

    //@Override
    public String getName() {
        return "SHStrategy";
    }
}
