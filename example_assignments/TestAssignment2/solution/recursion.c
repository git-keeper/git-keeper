#include <stdio.h>
#include <math.h>

int convertDecimalToOctal(int decimalNumber);
int convertBinarytoOctal(long long binaryNumber);


int main()
{
    int decimalNumber;
    
    printf("Enter a decimal number: ");
    scanf("%d", &decimalNumber);
    
    printf("%d in decimal = %d in octal", decimalNumber, convertDecimalToOctal(decimalNumber));
    
    return 0;
}

int convertDecimalToOctal(int decimalNumber)
{
    int octalNumber = 0, i = 1;
    
    while (decimalNumber != 0)
    {
        octalNumber += (decimalNumber % 8) * i;
        decimalNumber /= 8;
        i *= 10;
    }
    
    return octalNumber;
}



int convertBinarytoOctal(long long binaryNumber)
{
    int octalNumber = 0, decimalNumber = 0, i = 0;
    
    while(binaryNumber != 0)
    {
        decimalNumber += (binaryNumber%10) * pow(2,i);
        ++i;
        binaryNumber/=10;
    }
    
    i = 1;
    
    while (decimalNumber != 0)
    {
        octalNumber += (decimalNumber % 8) * i;
        decimalNumber /= 8;
        i *= 10;
    }
    
    return octalNumber;
}