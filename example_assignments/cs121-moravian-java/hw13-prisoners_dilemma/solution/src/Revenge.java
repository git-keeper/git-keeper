
public class Revenge implements Strategy {
    private char opponentLastPlay;

    public Revenge(){
        reset();
    }

    @Override
    public char play(){
        return opponentLastPlay;


    }
    @Override
    public void report (char opponentChoice){
        opponentLastPlay = opponentChoice;

    }
    @Override
    public void reset(){
        opponentLastPlay = 'd';

    }

    @Override
    public String getName(){
        return "First Defect";
    }

}
