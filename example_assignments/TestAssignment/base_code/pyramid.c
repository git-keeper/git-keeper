#include <stdio.h>
#include "string.h"

void pyramidGenerator(int n, char* symbol, char* string);
void StringPyramid ();


int main()
{
    int size;
    printf("Enter size of pyramid\n");
    scanf("%d",&size);
    
    char pyramid[] = "";
    char symbol[] = "X";
    
    pyramidGenerator(size, symbol, pyramid);
    printf("your pyramid: \n%s\n",pyramid);
    
    
    
    
}


void pyramidGenerator(int n, char* symbol, char* pyramid)
{
    
    int row, c, temp = n;
    
    for ( row = 1 ; row <= n ; row++ )
    {
        for ( c = 1 ; c < temp ; c++ )
            strcat(pyramid, " ");//printf(" ");
        
        temp--;
        
        for ( c = 1 ; c <= 2*row - 1 ; c++ )
            strcat(pyramid, symbol);//printf("*");
        
        strcat(pyramid, "\n");//printf("\n");
    }
    
    strcat(pyramid, "\0");
    
}



void StringPyramid ()
{
    int i,c,length;
    
    char arr[] = "Hello Everybody!";
    
    length = strlen(arr);
    
    for (i = length; i >= 0; i--)
    {
        printf("\n");
        for (c = 0; c < i; c++)
        {
            printf("%c",arr[c]);
        }
    }
    
}

