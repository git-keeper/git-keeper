/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * This strategy tries to determine which course is best to take against the
 * strategy it is currently competing with, always cooperate or always defect.
 * It does so by recording the opponents decision for the first ten moves
 * then bases its actions off of what the opponent did for the majority of its
 * moves.
 * @author yelito
 */
public class TatforTit implements Strategy{
    
    
    private char myDecision;
    private String name;


    
/**
 * Create a new TatforTit
 */    
    public TatforTit(){

        myDecision = 'D';

        name = "TatforTit";
        

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

        
        if(opponentChoice == 'D')
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
