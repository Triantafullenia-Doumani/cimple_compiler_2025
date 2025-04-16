#include <iostream>
using namespace std;

int main() {
L1: 
// Begin block factorial
L2: 
cout << "Type a number: ";
cin >> x;
L3: 
fact = 1;
L4: 
i = 1;
L5: 
if (i <= x) goto L7;
L6: 
goto L12;
L7: 
T_1 = fact * i;
L8: 
fact = T_1;
L9: 
T_2 = i + 1;
L10: 
i = T_2;
L11: 
goto L5;
L12: 
cout << fact << endl;
L13: 
return 0;
L14: 
// End block factorial
}