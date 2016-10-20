/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * This strategy recreates my strategy from the first semester.
 * This strategy starts by defecting. After this, it finds a random double
 * between 0 and 1 each turn and defects every time that number is less than
 * 0.7. The hope is that it will defect most of the time, but throw in a
 * cooperate here and there to throw off another strategy.
 * @author Nick
 */
public class NickStratFirstSemester implements Strategy{

    private char myDecision;
    private String name;

    
/**
 * Create a new NickStratFirstSemester
 */    
    public NickStratFirstSemester(){

        myDecision = 'D';

        name = "NickStratFirstSemester";
    }
    /**
     * This method returns the name of the strategy.
     * @return name the name of the strategy
     */

    public String getName(){

        return name;

    }

    /**
     * This method returns the decision for one turn of the game.
     * @return myDecision the decision of the strategy for this turn
     */

    public char play(){

        return myDecision;

    }

    /**
     * This method does the logic behind the strategy.
     * @param opponentChoice a char representing the opponents choice from
     * the last round
     */

    public void report(char opponentChoice){

        double val = Math.random();

        if(val > 0.7)
            myDecision = 'C';

        else
            myDecision = 'D';
    }

    /**
     *
     */

    public void reset(){

        myDecision = 'D';
    }


}






