/**
 * This class impletements the DoumithTitForTwoTats strategy.
 * It is similiar to TitForTat except that opponent must make the same choice
 * twice in a row before it is copied.
 * @author Aziz Doumith
 */
public class DoumithTitForTwoTats implements Strategy
{

    private char lastPlay;
    private boolean firstRoundPlayed;
    private char[] opponentLastTwoChoices;
    private int numRounds;

    /**
     * Creates a new DoumithTitForTwoTats strategy
     */
    public DoumithTitForTwoTats()
    {
        lastPlay = ' ';
        opponentLastTwoChoices = new char[2];
        firstRoundPlayed = false;
        numRounds = 0;
    }

    /**
     * Get the play for the current round
     * @return 'c' or 'd' based on the opponent's previous play
     */
    public char play()
    {
        numRounds += 1;
        /* For the first round we cooperate, after that we copy our opponents
         * play if the opponent repeated their play twice in a row.
         */
        if (!firstRoundPlayed)
        {
            firstRoundPlayed = true;
            lastPlay = 'c';
            return 'c';
        }
        else if (opponentLastTwoChoices[0] == 'd' && opponentLastTwoChoices[1]
                == 'd')
        {
            lastPlay = 'd';
            return 'd';
        }
        else if (opponentLastTwoChoices[0] == 'c' && opponentLastTwoChoices[1]
                == 'c')
        {
            lastPlay = 'c';
            return 'c';
        }
        //else
        return lastPlay;
    }

    /**
     * Report the result of the previous round
     * @param opponentChoice 'c' or 'd' based on the opponent's play
     */
    public void report(char opponentChoice)
    {
        //If there is an odd amount of rounds then we place the opponents play
        //in the 0th index of the opponentLastTwoChoices.
        if(numRounds % 2 == 1)
        {
            opponentLastTwoChoices[0] = opponentChoice;
            return;
        }
        //Else if there is an even amount of rounds then we place the opponents
        //play in the first index the opponentLastTwoChoices.
        opponentLastTwoChoices[1] = opponentChoice;
    }

    /**
     * Reset the strategy for a new game
     */
    public void reset()
    {
        lastPlay = ' ';
        opponentLastTwoChoices = new char[2];
        firstRoundPlayed = false;
        numRounds = 0;
    }

    /**
     * Get the name of the strategy
     * @return "DoumithTitForTwoTats"
     */
    public String getName()
    {
        return "DoumithTitForTwoTats";
    }
}
