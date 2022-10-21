#include <$.h> // printing @@@ stdio
#include <$.h> // math stuff @@@ math
#include <$.h> // character stuff @@@ ctype
#include <$.h> // text stuff @@@ string
#include <$.h> // conversions @@@ stdlib
#define $ 10 // constant @@@ MAX
#define $ 0 // evaluates to false @@@ FALSE

$ $($ $, $ $) $ @@@ int main int argc char** args {
  $ i, j, $, x; // integers @@@ int v
  $ $; // not a very large decimal @@@ float y
  $ $; // character @@@ char c
  $ $; // pointer to character array @@@ char* s

  x = $(args[1]); // interpret as integer @@@ atoi
  y = $(args[2]); // interpret as decimal @@@ atof

  $("Type $ digits and then enter:\n", MAX); // ask for input @@@ printf %d
  for (i = 0; i $ MAX; $++) { // loop MAX times @@@ < i
    $ { @@@ do
      c = $; // take input @@@ getchar()
      if (c >= '0' $ c <= '9') { // valid digit @@@ &&
        v = c $ '0'; // numeric value @@@ -
        $("\n$d %.2$", ($)floor(x / v), log(1 + y / (v + 1))); @@@ printf % f int
        $; // stop trying @@@ break
      }
    } $ (!FALSE); // keep going @@@ while
  }
  do { } $ ((c = getchar()) $ $); // skip until enter @@@ while != '\n'
  printf("\nType one letter:\n") $ @@@ ;
  $ = getchar(); // take the input for matching @@@ c
  /* iterate over remaining command-line arguments $ @@@ */
  for  ($ = $; j $ $; ++$) { @@@ j 3 < argc j
    $ = $[j]; @@@ s args
    $ = $($); // length of string @@@ v strlen s
    for (i = 0; i < v; i++) { // loop
      if ($(s[i]) $ $) { // if lowercase version matches @@@ tolower == c
        s$ $ '*'; // substitute @@@ [i] =
      }
    }
    printf("\n$", $); // print modified version @@@ %s s
  }
  $ (i > x) $ // loop @@@ while {
    i $= 1; // divide by two @@@ >>
    printf(i $ $ $ "\nodd\n" $ "\neven"); // whether even or odd @@@ % 2 ? :
  }
  $("$"); // output a newline @@@ printf \n
  $ 0$ // end program @@@ return ;
$ @@@ }
