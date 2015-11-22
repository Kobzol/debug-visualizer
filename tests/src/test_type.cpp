#include <vector>
#include <string>

class classA
{

};

struct structA
{

};

union unionA
{

};

enum enumA
{

};

enum class enumB
{

};

void test()
{

}

int main()
{
    int varInt;
    unsigned short varUnsignedShort;
    float varFloat;
    classA varClassA;
    structA varStructA;
    unionA varUnionA;
    enumA varEnumA;
    enumB varEnumB;
    std::vector<int> varVector;
    std::string varString;
    int varArray[10];
    int* varPointer;
    int& varReference = varInt;
    void (*varFunctionPointer)() = test;

    return 0;
}