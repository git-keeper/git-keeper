/**
 * This class implements the strategy that always defects
 *
 * @author mebjc01
 */
public class newStrategy implements Strategy {
    private char opponenet;
    private char me;
    public int count=0;
    public int Ocount=0;
    /**
     * Get the play for the current round
     *
     * return char
     */
    public char play() {
        if (count ==0){
            Ocount+=1;
            count+=1;
            me= 'd';
        }
        else if (count==1){
            if (opponenet=='c') {
                count+=1;
                me = 'c';
            }
            else if (opponenet=='d'){
                Ocount+=1;
                count+=1;
                me= 'd';
            }
        }
        else if(count==2) {
            if (Ocount == 2) {
                Ocount+=1;
                count+=1;
                me= 'd';
            }
            else {
                count += 1;
                me = 'c';
            }
        }
        else if(count==3) {
            if (Ocount > 2) {
                count += 1;
                me = 'd';
            }
            else{
                count += 1;
                me = 'c';
            }
        }
        else {
            count += 1;
            me = 'c';
        }
        return me;
    }

    /**
     * report the result of the previous round
     *
     * @param opponentChoice 'c' or 'd' based on the opponent's play
     */
    public void report(char opponentChoice) {
        opponenet=opponentChoice;

    }

    /**
     * Reset the strategy for a new game
     */
    public void reset() {
        count=0;
    }

    /**
     * Get the name of this strategy
     *
     * @return "A string"
     */
    public String getName() {
        return "Makeshift";
    }
    public int getCount() {
        return count;
    }

}
