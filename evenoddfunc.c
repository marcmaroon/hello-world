// create a function that checks if a number is even or odd
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>



bool evenodd(int x){
    return x % 2 == 0;
}

int main(int argc, char* argv[]){
    if (argc != 2)
    {
        printf("incorrect amount of arguments\n");
        exit(9);
    }

    int num = atoi(argv[1]);

    bool result = evenodd(num);

    printf("%d\n", num);
    if(result)
    {
        printf("even\n");

    }
    else
    {
        printf("odd\n");
    }

}