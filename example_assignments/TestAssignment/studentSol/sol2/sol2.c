#include <stdio.h>
 
int main()
{
   int row, c, n, temp;
 
   printf("Enter size of pyramid");
   scanf("%d",&n);
 
   temp = n;
 
   for ( row = 1 ; n >= row ; row++ ) // changed  row <= n
   {
      for ( c = 1 ; c < temp ; c++ )
         printf(" ");
 
      temp--;
 
      for ( c = 1 ; c <= 2*row - 1 ; c++ )
         printf("*");
 
      printf("\n");
   }
 
   return 0;
}
