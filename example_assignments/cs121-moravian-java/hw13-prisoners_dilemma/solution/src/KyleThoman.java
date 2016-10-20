/**
 * Created by johnpolich on 4/4/16.
 */
public class KyleThoman implements Strategy {
        private char opponentLastPlay;
        int turns = 0;
        int defects = 0;
        int cooperates = 0;
        public KyleThoman() {
            reset();
        }

        @Override
        public char play() {
            if(opponentLastPlay == 'c') {
                cooperates++;
            }
            else{
                defects++;
            }
            if(turns < 6){
                turns++;
                return opponentLastPlay;
            }
            if(defects>cooperates){
                return 'd';
            }
            else{
                return 'c';
            }
        }

        @Override
        public void report(char opponentChoice) {
            opponentLastPlay = opponentChoice;
        }

        @Override
        public void reset() {
            opponentLastPlay = 'c';
        }

        @Override
        public String getName() {
            return "KyleThoman";
        }
    }

