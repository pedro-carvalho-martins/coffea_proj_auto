#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>

int main ( int argc, char *argv[] )
{

  int i;
  int nPulses;

  int msPulse = 80;
  int msBetweenPulses = 320;

  printf("%d arguments\n",argc);

  if (argc == 2){

    nPulses = atoi(argv[1]);

    wiringPiSetup() ;
    pinMode (29, OUTPUT) ;

    for (i=0; i<nPulses; i++)
    {
      digitalWrite (29, HIGH) ; delay (msPulse) ;
      digitalWrite (29,  LOW) ; delay (msBetweenPulses) ;
      printf("iterationDebug\n");
    }

    return 0 ;

  }

  return -1 ;

}