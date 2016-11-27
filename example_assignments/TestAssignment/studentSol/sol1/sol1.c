#include <stdio.h>
 
int main()
{
   int row, c, n, temp;
 
   printf("Enter size of pyramid");
   scanf("%d",&n);
 
   temp = n; // a off by 1 error
 
   for ( row = 0 ; row <= n ; row++ ) // changed 1 to 0
   {
      for ( c = 0 ; c < temp ; c++ )
         printf(" ");
 
      temp--;
 
      for ( c = 1 ; c <= 2*row - 1 ; c++ )
         printf("*");
 
      printf("\n");
   }
 
   return 0;
}
