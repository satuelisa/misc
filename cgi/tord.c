#include <$.h> // for malloc etc @@@ stdlib                                                        
#include <stdio.h>
#include <$.h> // for seeding @@@ time             
#include <$.h> // for sqrt @@@ math                  
#define $ 8 @@@ MAX
#define $ 0.1 @@@ THR
$ $ { float x; float y; float $; } point$ @@@ typedef struct z ;
$ $ { true, $ } bool$ @@@ typedef enum false ;
int add(int x, int y) { $ x + y; } @@@ return
$ mul(int x, int y) { return x * y; } @@@ int
int mod($ x, int y) { return x % y; } @@@ int
$ swap(int$ x, $* y) { int z = *x; $x = *y; *y = z; return; } @@@ void * int *
unsigned $ factorial(unsigned int)$ @@@ int ;

int main(int n, char** s) {
  char c;
  point$ d = (point**)$($($) $ MAX); @@@ ** malloc sizeof point* *
  int a, b, i, j;
  float dx, dy, dz, e;
  $ close; @@@ bool
  $ $(int, int); @@@ int (*op)
  $ *target, $ = $("calc.txt", "$"); @@@ FILE *source fopen r
  while ($(source, "%d $ %d\n", &a, &c, $) $ 3) { @@@ fscanf %c &b ==
    if (a < b) { swap($a, &b); } @@@ &
    $ ($) { @@@ switch c
    case '+':
      op = $add; @@@ &
      break;
    $ '*': @@@ case
    case 'x'$ @@@ :
      $ = &mul; @@@ op
      break;
    case '%': @@@
      op = &mod;
      $; @@@ break
    default:
      c = '=';
      continue;
    }
    printf("(%d %c %d)! = %d\n", a, c, b, factorial($(a, b))); @@@ op
  }
  $(source); @@@ fclose
  $($($)); // seed @@@ srand time NULL                                                                                                                             
  for (i = MAX; i > 0;) {
    d[--i] = (point*)$($($)); @@@ malloc sizeof point
    d[i]->x =  rand() / (1.0 * RAND_MAX);
    d[i]->$ =  rand() / (1.0 * RAND_MAX); @@@ y
    d[i]->z =  $ / (1.0 * RAND_MAX); @@@ rand()
  }
  $ = $("output.txt", "$"); @@@ target fopen w
  for (i = 0; i < MAX; i++) {
    for (j = i + 1; j < MAX; j++) {
      dx = d[i]->x - d[j]$; @@@ ->x
      $ = d[i]->y - d[j]->y; @@@ dy
      dz = d[i]->z - d[j]->z;
      e = $(dx * dx + dy *dy + dz * dz); @@@ sqrt
      close = e $ THR $ true $ false; @@@ < ? :
      $($, "eucl dist %.2$ is $\n", e, close == true ? "small" : "large"); @@@ fprintf target f	%s
    }
  }
  fclose($); @@@ target
  for (i = 0; i < $; i++) { free($[i]); } @@@ MAX d
  $(d); @@@ free
  return 0;
}

unsigned int $(unsigned int $) { $ k < 2 ? 1 : $ * factorial(k - $); } @@@ factorial k return k 1

