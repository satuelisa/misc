#!/usr/bin/env python3
import cgi, os
import cgitb; cgitb.enable()
from os import chmod
from random import randint
from sys import argv, stdout, stderr
from xml.dom import minidom
from subprocess import check_call, Popen, CalledProcessError, check_output
import datetime

forbidden = ['system', 'fopen', 'define', 'while', 'for']
LOC = '/var/www/html/elisa/'

def safe(expression):
   try:
      semicolon = expression.index(';')
      expression = expression[:semicolon].strip()
   except:
      pass
   for blocked in forbidden:
      if blocked in expression:
         return ''
   return expression.strip()

def output(filename, fields):
   with open(filename, 'w') as target:
      print('<xml>', file = target)
      for label in fields:
         print("<field><id>%s</id><value><![CDATA[%s]]></value></field>" % (label, fields[label]), file = target)
      print('</xml>', file = target)
   return

def fill(target, filename):
   source = minidom.parse(filename)
   fields = source.getElementsByTagName('field')
   for field in fields:
      label = field.childNodes[0].firstChild.data
      value = field.childNodes[1].firstChild.data
      label = label.encode('ascii', 'ignore')
      value = value.encode('ascii', 'ignore')
      target[label.decode('utf-8')] = value.decode('utf-8') 
   return

defs = { \
   'r2.1':  '(int)(floor(log(a) / log(BASE)) + 1)', \
   'r2.2' : '((x | (1 << k)) & (~(1 << (k / 2))))', \
   'r2.3': 'log(p) > sqrt(q) ? "log of p\\n" : "sqrt of q\\n"', \
   'r4.1': 'return gcd(y, x % y)', \
   'r4.2': 'pal(s, 0, len(s) - 1) > 0', \
   'r6.1': 'high, low, dif / 2', \
   'r6.2': '(int*)malloc(sizeof(int) * n)', \
   'r7.1': '!feof(input)', \
   'r7.2': "fgetc(input) == '\\n'", \
   'r7.3': 'fscanf(input, "%7s %3s %d\\n", student, program, &grade)' }

def preptime(target):
   print('#include <stdint.h>', file = target)
   print('#include <time.h>', file = target)
   print('#define ABORTED 42', file = target)
   print('clock_t start;', file = target)

def checktime(target):
   print('  extern clock_t start;', file = target)

def starttime(target):
   print('  extern clock_t start;', file = target)
   print('  start = clock();', file = target)

def endtime(target):
   print('    if ((clock() - start) / CLOCKS_PER_SEC > 3) {', file = target)
   print('      return ABORTED;', file = target)
   print('    }', file = target)

def source1_1(targets, generated, fill):
   # printout
   for target in targets:    
      print('#include <stdio.h>', file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  float x = %s;' % generated['1.X'], file = target)
      print('  int y = %s;' % generated['1.Y'], file = target)
      starttime(target)
      print('  while (x <= y) {', file = target)
      print('    x = x / %s;' % generated['1.Z'], file = target)
      print('    y = y * x;', file = target)
      endtime(target)
      print('  }', file = target)
      print('  printf("%.2f, %d\\n", x, y);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r1.1"]]
   
def source1_2(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  int i;', file = target)
      print('  int a = %s;' % generated['1.A'], file = target)
      print('  int b = %s;' % generated['1.B'], file = target)
      print('  int c = %s;' % generated['1.C'], file = target)
      starttime(target)
      print('  for (i = a; i >= b; i = i - c) {', file = target)
      endtime(target)
      print('  }', file = target)
      print('  printf("%d\\n", i);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r1.2"]]
      
def source1_3(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      print('#define FROM %s' % generated['1.F'], file = target)
      print('#define TO %s' % generated['1.T'], file = target)
      print('#define STEP %s' % generated['1.S'], file = target)
      print('#define EVEN 0', file = target)
      preptime(target)
      print('int parity(int v);', file = target)
      print('int main() {', file = target)
      print('  int j;', file = target)
      print('  int count = 0;', file = target)
      starttime(target)
      print('  for (j = FROM; j < TO; j = j + STEP) {', file = target)
      endtime(target)
      print('    if (parity(j) == EVEN) {', file = target)
      print('      count = count + 1;', file = target)
      print('    }', file = target)
      print('  }', file = target)
      print('  printf("%d\\n", count);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
      print('int parity(int v) {', file = target)
      print('  return v % 2;', file = target)
      print('}', file = target)
   return [fill[0]["r1.3"]]
      
def source2_1(targets, generated, fill):
   # expression
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      print('#include <stdlib.h>', file = target)
      print('#include <math.h>', file = target)
      print('#define BASE %s' % generated['2.base'], file = target)
      print('int main() {', file = target)
      print('  int i, a, d;', file = target)
      print('  for (i = 0; i < 100; i++) {', file = target)
      print('    a = rand() % 500000; // any', file = target)
      print('    d = %s;' % data['r2.1'], file = target)
      print('    printf("%d needs %d digits in base %d\\n", a, d, BASE);', file = target)
      print('  }', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []

def source2_2(targets, generated, fill):
   # expression
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      print('#include <stdlib.h>', file = target)
      print('int main() {', file = target)
      print('  int x, y, i;', file = target)
      print('  int k = %s;' % generated['2.k'], file = target)
      print('  for (i = 0; i < 100; i++) {', file = target)
      print('    x = rand() % 500000; // any', file = target)
      print('    y = %s;' % data['r2.2'], file = target)
      print('    printf("%d -> %d\\n", x, y);', file = target)
      print('  }', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []

def source2_3(targets, generated, fill):
   # expression
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]['r2.3']
      print('#include <stdio.h>', file = target)
      print('#include <stdlib.h>', file = target)
      print('#include <math.h>', file = target)
      print('int main() {', file = target)
      print('  double p, q, t;', file = target)
      print('  int i;', file = target)
      print('  for (i = 0; i < 100; i++) {', file = target)
      print('     p = 124.5 * (rand() % 500);', file = target)
      print('     q = 0.7 * (rand() % 5000);', file = target)
      print('     if (rand() % 2 == 0) {', file = target)
      print('        t = p;', file = target)
      print('        p = q;', file = target)
      print('        q = t;', file = target)
      print('      }', file = target)
      print(f'     printf({data});', file = target)
      print('  }', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []

def source3_1(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      print('#define START %s' % generated['3.A'], file = target)
      print('#define STOP %s' % generated['3.B'], file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  int i = START;', file = target)
      print('  int count = 0;', file = target)
      starttime(target)
      print('  do {', file = target)
      print('    ++count;', file = target)
      endtime(target)
      print('  } while (i-- != STOP);', file = target)
      print('  printf("%d\\n", count);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r3.1"]]

def source3_2(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      print('#define START %s' % generated['3.A'], file = target)
      print('#define STOP %s' % generated['3.B'], file = target)
      print('#define MOD %s' % generated['3.C'], file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  int i = START;', file = target)
      print('  int count = 0;', file = target)
      starttime(target)
      print('  do {', file = target)
      endtime(target)
      print('    ++count;', file = target)
      print('    if (count % MOD == 0) {', file = target)
      print('      break;', file = target)
      print('    }', file = target)
      print('  } while (i-- != STOP);', file = target)
      print('  printf("%d\\n", count);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r3.2"]]

def source3_3(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      print('#define START %s' % generated['3.A'], file = target)
      print('#define STOP %s' % generated['3.B'], file = target)
      print('#define MOD %s' % generated['3.C'], file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  int i = START;', file = target)
      print('  int count = 0;', file = target)
      starttime(target)
      print('  do {', file = target)
      endtime(target)
      print('    if (i % MOD == 0) {', file = target)
      print('      count /= 2;', file = target)
      print('      continue;', file = target)
      print('    }', file = target)
      print('    ++count;', file = target)
      print('  } while (i-- > STOP);', file = target)
      print('  printf("%d\\n", count);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r3.3"]]

def source4_1(targets, generated, fill):
   # expression
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      print('#include <stdlib.h>', file = target)
      print('int gcd(int x, int y);', file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  int a, b, i;', file = target)
      starttime(target)
      print('  for (i = 0; i < 100; i++) {', file = target)
      print('     a = 100 + rand() % 200; // any', file = target)
      print('     b = 10 + rand() % 150; // any', file = target)
      print('     printf("%d\\n", gcd(a > b ? a : b, b > a ? a : b));', file = target)
      print('  }', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
      print('int gcd(int x, int y) {', file = target)
      checktime(target)
      print('  if (y == 0) {', file = target)
      print('    return x;', file = target)
      print('  }', file = target)
      endtime(target)
      print('  %s;' % data['r4.1'], file = target)
      print('}', file = target)
   return []

def source4_2(targets, generated, fill):
   # expression
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      print('#define FALSE 0', file = target)
      print('#define TRUE 1', file = target)
      print('int len(char* s);', file = target)
      print('int pal(char* t, int s, int e);', file = target)
      print('int main() {', file = target)
      print('  char* s = "saippuakauppias"; // any', file = target)
      print('  printf("%%s\\n", %s ? "yes" : "no");' % data['r4.2'], file = target)
      print('  s = "otracosa"; // any', file = target)
      print('  printf("%%s\\n", %s ? "yes" : "no");' % data['r4.2'], file = target)
      print('  return 0;', file = target)
      print('}', file = target)
      print('int len(char* s) {', file = target)
      print('  int n = 0;', file = target)
      print("  while (s[n] != '\\0') {", file = target)
      print('    n++;', file = target)
      print('  }', file = target)
      print('  return n;', file = target)
      print('}', file = target)
      print('int pal(char *t, int s, int e) {', file = target)
      print('  if (s >= e) {', file = target)
      print('    return TRUE;', file = target)
      print('  }', file = target)
      print('  if (t[s] == t[e]) {', file = target)
      print('    return pal(t, ++s, --e);', file = target)
      print('  }', file = target)
      print('  return FALSE;', file = target)
      print('}', file = target)
   return []
      
def source4_3(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      print('#include <math.h>', file = target)
      print('#define NONE 1', file = target)
      print('#ifdef NONE', file = target)
      print('int p(int x, int y) { return x << (y - 1); }', file = target)
      print('#else', file = target)
      print('int p(int x, int y) { return (int)pow(x, y); }', file = target)
      print('#endif', file = target)
      print('int main() {', file = target)
      print('  int a = %s;' % generated['4.A'], file = target)
      print('  int b = %s;' % generated['4.B'], file = target)
      print('  printf("%d %d\\n", p(a, b), p(b, a));', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r4.3"]]

def source5_1(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      print('int f(int x) {', file = target)
      print('  return x << 1;', file = target)
      print('}', file = target)
      print('void g(int* x) {', file = target)
      print('  *x *= 2;', file = target)
      print('}', file = target)
      print('int main() {', file = target)
      print('  int a = %s;' % generated['5.A'], file = target)
      print('  int b = f(a);', file = target)
      print('  g(&a);', file = target)
      print('  printf("%d\\n", a == b);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r5.1"]]

def source5_2(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  char* t = "hello, world";', file = target)
      print("  char c = '%s';" % generated['5.C'], file = target)
      print('  char* s = t;', file = target)
      starttime(target)
      print("  while (s[0] != '\\0') {", file = target)
      print('    if (s[0] == c) {', file = target)
      print('      ++s;', file = target)
      print('      break;', file = target)
      print('    }', file = target)
      print('    s++;', file = target)
      endtime(target)
      print('  }', file = target)
      print('  printf("[%s]\\n", s);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r5.2"]]
   
def source5_3(targets, generated, fill):
   # printout
   for target in targets:
      print('#include <stdio.h>', file = target)
      print('int odd(int* data, int l) {', file = target)
      print('  return data[l/2];', file = target)
      print('}', file = target)
      print('int even(int* data, int l) {', file = target)
      print('  return (data[l/2] + data[l/2 + 1]) / 2;', file = target)
      print('}', file = target)
      print('int routine(int*, int);', file = target)
      print('int main() {', file = target)
      print('  int missing = %s;' % generated['5.X'], file = target)
      print('  int data[] = {2, 5, 6, 12, missing, 84, 333, 415};', file = target)
      print('  int length = 8;', file = target)
      print('  int(*use)(int*, int);', file = target)
      print('  switch (length % 2) {', file = target)
      print('  case 0:', file = target)
      print('    use = even;', file = target)
      print('    break;', file = target)
      print('  case 1:', file = target)
      print('    use = odd;', file = target)
      print('    break;', file = target)
      print('  }', file = target)
      print('  printf("%d\\n", use(data, length));', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return [fill[0]["r5.3"]]

def source6_1(targets, generated, fill):
   # expression
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      print('typedef struct account {', file = target)
      print('  char* username;', file = target)
      print('  double balance;', file = target)
      print('} acc;', file = target)
      print('void transfer(acc* from, acc* to, double amount) {', file = target)
      print('  if (from->balance > amount) {', file = target)
      print('    to->balance += amount;', file = target)
      print('    from->balance -= amount;', file = target)
      print('  }', file = target)
      print('}', file = target)
      print('void display(acc x) {', file = target)
      print('  printf("%s, balance %.2f\\n", x.username, x.balance);', file = target)
      print('}', file = target)
      print('int main() {', file = target)
      print('  acc a = {"foo", %s.0};' % generated['6.A'], file = target)
      print('  acc b = {"bar", %s.0};' % generated['6.B'], file = target)
      print('  acc* high = (a.balance > b.balance) ? &a : &b;', file = target)
      print('  acc* low = (a.balance < b.balance) ? &a : &b;', file = target)
      print('  double dif = high->balance - low->balance;', file = target)
      print('  transfer(%s);' % data['r6.1'], file = target)
      print('  display(a);', file = target)
      print('  display(b);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []

def source6_2(targets, generated, fill):
   # expression
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      print('#include <stdlib.h>', file = target)
      print('int comp(const void* x, const void* y) {', file = target)
      print('  return *(int*)x - *(int*)y;', file = target)
      print('}', file = target)
      print('main(int c, char* v[]) {', file = target)
      print('  if (c > 1) {', file = target)
      print('    int i, n = atoi(v[1]);', file = target)
      print('    int* data = %s;' % data['r6.2'], file = target)
      print('    for (i = 0; i < n; i++) {', file = target)
      print('      data[i] = rand() % 10;', file = target)
      print('    }', file = target)
      print('    qsort(data, n, sizeof(int), comp);', file = target)
      print('    int prev = -1;', file = target)
      print('    for (i = 0; i < n; i++) {', file = target)
      print('      if (data[i] != prev) {', file = target)
      print('	       printf("%d ", data[i]);', file = target)
      print('	       prev = data[i];', file = target)
      print('      }', file = target)
      print('    }', file = target)
      print('    printf("\\n");', file = target)
      print('    free(data);', file = target)
      print('  }', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []
   
def source6_3(targets, generated, fill):
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      print('#include <stdio.h>', file = target)
      print('#define READ 01', file = target)
      print('#define WRITE 02', file = target)
      print('#define EXECUTE 04', file = target)
      print('typedef enum {FALSE = 0, TRUE = 1} boolean;', file = target)
      print('int main(int x, char* y[]) {', file = target)
      print('  int i;', file = target)
      print('  for (i = 1; i < x; i++) {', file = target)
      print('    unsigned int status = 0;', file = target)
      print('    char* pos = y[i];', file = target)
      print('    boolean done = FALSE;', file = target)
      print('    while (!done) {', file = target)
      print('      switch (pos[0]) {', file = target)
      print("      case '\\0':", file = target)
      print('	       done = TRUE;', file = target)
      print('	       break;', file = target)
      print("      case 'r':", file = target)
      print('	       status |= READ;', file = target)
      print('	       break;', file = target)
      print("      case 'w':", file = target)
      print('	       status |= WRITE;', file = target)
      print('	       break;', file = target)
      print("      case 'x':", file = target)
      print('	       status |= EXECUTE;', file = target)
      print('	       break;', file = target)
      print('      default:', file = target)
      print('	       break;', file = target)
      print('      }', file = target)
      print('      pos++;', file = target)
      print('    }', file = target)
      print('    printf("%d ", status);', file = target)
      print('  }', file = target)
      print('  printf("\\n");', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []
   
def source7_12(targets, generated, fill):
   # expressions
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      print('#include <ctype.h>', file = target)
      print('#define CAPACITY 80', file = target)
      print('#define INCOMPLETE -1', file = target)
      print('#define UNDEFINED INCOMPLETE ', file = target)
      preptime(target)
      print('int count(char* file) {', file = target)
      print('  int count = UNDEFINED;', file = target)
      print('  FILE* input = fopen(file, "r");', file = target)
      print('  if (input) {', file = target)
      starttime(target)
      try:
         print('    while (%s) {' % data['r7.1'], file = target)
      except:
         pass
      endtime(target)
      try:
         print('      if (%s) {' % data['r7.2'], file = target)
      except:
         pass
      print('	       count++;', file = target)
      print('      }', file = target)
      print('    }', file = target)
      print('    count++; // last line', file = target)
      print('  }', file = target)
      print('  fclose(input);', file = target)
      print('  return count;', file = target)
      print('}', file = target)
      print('int main() {', file = target)
      print('  char* filename = "/var/www/html/elisa/data/ansic/registered.txt";', file = target)
      print('  int c = count(filename);', file = target)
      print('  if (c != UNDEFINED) {', file = target)
      print('    printf("File [%s] has %d lines.\\n", filename, c);', file = target)
      print('  } else {', file = target)
      print('    fprintf(stderr, "No such readable file.\\n");', file = target)
      print('  }', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []
      
def source7_3(targets, generated, fill):
   # expression
   assert len(targets) == len(fill)
   for pos in range(len(targets)):
      target = targets[pos]
      data = fill[pos]
      print('#include <stdio.h>', file = target)
      preptime(target)
      print('int main() {', file = target)
      print('  FILE* input = fopen("/var/www/html/elisa/data/ansic/id.dat", "r");', file = target)
      print('  char student[8];', file = target)
      print('  char program[4];', file = target)
      print('  int grade;', file = target)
      starttime(target)
      print('  while (!feof(input)) {', file = target)
      print('    %s;' % data['r7.3'], file = target)
      print('    printf("someone from %s got %d\\n", program, grade);', file = target)
      endtime(target)
      print('  }', file = target)
      print('  fclose(input);', file = target)
      print('  return 0;', file = target)
      print('}', file = target)
   return []

generator = { \
   "r1.1": source1_1, \
   "r1.2": source1_2, \
   "r1.3": source1_3, \
   "r2.1": source2_1, \
   "r2.2": source2_2, \
   "r2.3": source2_3, \
   "r3.1": source3_1, \
   "r3.2": source3_2, \
   "r3.3": source3_3, \
   "r4.1": source4_1, \
   "r4.2": source4_2, \
   "r4.3": source4_3, \
   "r5.1": source5_1, \
   "r5.2": source5_2, \
   "r5.3": source5_3, \
   "r6.1": source6_1, \
   "r6.2": source6_2, \
   "r6.3": source6_3, \
   "r7.1": source7_12, \
   "r7.2": source7_12, \
   "r7.3": source7_3 }

def grade(label, generated, submitted, h, log):
   execs = ['/var/www/html/elisa/data/ansic/%s_%s.exe' % (h, label)]
   targets = ['/var/www/html/elisa/data/ansic/%s_%s.c' % (h, label)]
   handles = [open(targets[0], 'w')]
   fill = [submitted]
   if label in defs or label == 'r6.3': # expression  
      print('Comparing outputs after inserting expressions.', file = log)
      fill.append(defs)
      targets.append(f'/var/www/html/elisa/data/ansic/{h}_{label}_def.c')
      handles.append(open(targets[-1], 'w'))
      execs.append(f'/var/www/html/elisa/data/ansic/{h}_{label}.def')
   args = ['', '']
   if label == 'r6.2':
      v = '%d' % randint(5, 10)
      args = [v, v]
   if label == 'r6.3':
      arg = []
      for token in generated['6.args'].split():
         a = ''
         numerical = int(token)
         if numerical & 1:
            a += 'r'
         if numerical & 2:
            a += 'w'
         if numerical & 4:
            a += 'x'
         arg.append(a)
         args = [submitted['r6.3'].split(), arg]
   assert len(handles) == len(fill)
   print(f'Generating a template using {fill[0][label]}', file = log)
   outputs = generator[label](handles, generated, fill)
   print(f'Outputs: {outputs}', file = log)
   for pos in range(len(targets)):
      print(f'Compiling {targets[pos]}...', file = log)
      handles[pos].close()
      try:
         check_call(['/usr/bin/gcc', '-lm', '-o', execs[pos], targets[pos]])
      except CalledProcessError as e:
         print(f'Error al compilar {targets[pos]}: {e}', file = log)
         break
      try:
         print(f'Executing {execs[pos]} with {args}', file = log)
         parameters = [execs[pos]]
         for a in args[pos]:
            parameters.append(a)
         outputs.append(check_output(parameters).strip().decode("utf-8") )
      except CalledProcessError as e:
         print(f'Error al ejecutar {execs[pos]}: {e}', file = log)
         #break
   print(f'Outputs: {outputs}', file = log)
   if len(outputs) != 2: 
      return False
   print(outputs)
   return outputs[0].strip() == outputs[1].strip() # the outputs are equal

def main():
   print('Content-type: text/html\n\n')
   print('<html>')
   print('<head><title>Grading completed</title></head>')
   print('<body><span style="color:red">')
   print('<p>No-one actually needs to see this.</p>')
   hash = None
   form = None
   timestamp = str(datetime.datetime.now()).split('.')[0]
   print('<h2>Script reply</h2><p>')
   print('Activated', timestamp, '<br />')
   form = cgi.FieldStorage()
   hash = form.getvalue('hash')
   if hash is None:
      try:
         student = argv[1] # debug mode
      except:
         print('No hash nor student info <br />')
         return
   if hash is None: # debug mode
        hash = hashlib.md5(student.encode("utf-8")).hexdigest()
   print('hash', hash, '<br />')
   filename = LOC + 'teaching/prog/ansic/data/%s' % hash
   status = dict()
   fill(status, '%s.awarded.xml' % filename)
   accepted = dict()
   fill(accepted, '%s.accepted.xml' % filename)
   rejected = dict()
   fill(rejected, '%s.rejected.xml' % filename)
   attempts = dict()
   fill(attempts, '%s.attempts.xml' % filename)
   generated = dict()
   fill(generated, '%s.generated.xml' % filename)
   with open(LOC + 'data/ansic/%s.log' % hash, 'a') as log:
      print('<session>\nSubmission of %s at %s' % (hash, timestamp), file = log)
      submitted = dict()
      for label in form.keys():
         if label == 'hash':
            continue # not a response
         if label[0] != 'r':
            continue # not a response
         response = form.getvalue(label)
         if response is not None:
            response = safe(response)
            if len(response) > 0:
               print("Received '%s' for %s." % (response, label), file = log)
               print("Received '%s' for %s." % (response, label))
               submitted[label] = response
      for exercise in submitted:
         if exercise not in attempts:
            attempts[exercise] = "1"
         else:
            attempts[exercise] = int(attempts[exercise]) + 1
         print(f'Grading {submitted[exercise]} for {exercise}...', file = log)
         if grade(exercise, generated, submitted, hash, log): # correct
            print('Correct')
            print("This is correct.", file = log)
            status[exercise] = "1"
            print("Storing the accepted response.", file = log)            
            accepted[exercise] = submitted[exercise]
            if exercise in rejected:
               del rejected[exercise]
         else:
            print("This is incorrect.", file = log)
            status[exercise] = "0"
            print("Storing the rejected response.", file = log)
            rejected[exercise] = submitted[exercise]
      output('%s.awarded.xml' % filename, status)
      output('%s.accepted.xml' % filename, accepted)
      output('%s.rejected.xml' % filename, rejected)
      output('%s.attempts.xml' % filename, attempts)
      print("XML storage updated.", file = log)                  
      print('</session>', file = log)
   print('</p>')
   print('</span></body>')
   print('</html>')
   return

if __name__ == "__main__":
    main()

