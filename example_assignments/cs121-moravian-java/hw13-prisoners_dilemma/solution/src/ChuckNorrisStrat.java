/**
 * In the true fashion of Chuck Norris, this strategy reads and reacts to the
 * opposing strategies. It does so by defecting for 5 turns, then using the
 * titfortat strategy for 5 turns. It keep track of how 
 * many years it gets for the two sections, then uses whichever performed the 
 * best for the remaining turns.
 * @author yelito
 */
public class ChuckNorrisStrat implements Strategy{
    
    private char myDecision;
    private String name;
    private int count;
    
    private int myTimeD;
    private int myTimeTT;
    

/**
 * Create a new ChuckNorrisStrat
 */
    public ChuckNorrisStrat(){

        myDecision = 'D';

        name = "ChuckNorrisStrat";
        
        myTimeD = 0;
        myTimeTT = 0;
        
        count = 0;
        

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

        
        
       // Record the years for the first 5 turns and the second 5 turns.
        if(myDecision == 'C' && opponentChoice == 'C'){

            if(count < 5)
                myTimeD += .5;
            
            else
                myTimeTT += .5;


        }

        else if(myDecision == 'C' && opponentChoice == 'D'){

            if(count < 5)
                myTimeD += 10;
            
            else
                myTimeTT += 10;

        }

        else if(myDecision == 'D' && opponentChoice == 'C'){

            if(count < 5)
                myTimeD += 0;
            
            else
                myTimeTT += 0;
        }

        else if(myDecision == 'D' && opponentChoice == 'D'){

            if(count < 5)
                myTimeD += 5;
            
            else
                myTimeTT += 5;

        }
        
       // Begin the game by defecting 5 times and titfortatting 5 times.
       if(count < 5)
          myDecision = 'D';
        
       else if(count >= 5 && count < 10){
           
            if(opponentChoice == 'D')
                myDecision = 'D';

            else
                myDecision = 'C';
       }
        
       else if(count >= 10){
           
       // After those 10 turns, decide which strategy was better and use 
       // that for the rest of the game.
            
           if(myTimeD < myTimeTT)
               myDecision = 'D';
           
           // I decide to use TitforTat if myTimeTT is >= myTimeD because it is
           // a better strategy in most cases.
           else{
            
           
               if(opponentChoice == 'D')
                    myDecision = 'D';

               else
                    myDecision = 'C';
           }
       }
               
        
        
        count++;
        
    }

    /**
     * Reset any necessary variables to thier original value.
     */

    public void reset(){
        
        // I choose not to reset my count and time variables so the strategy
        // will continue using the best option strategy for the rest of the 
        // game rather than having to check which is best every turn.
        
        myDecision = 'D';
        
    }

}
