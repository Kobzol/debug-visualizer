#include <vector>
#include <string>

struct structA
{
    int x;
    std::string y;
};

class classA
{
public:
    structA str;
    std::vector<int> vec;

    void test() { }
};

union unionA
{
public:
    int a;
    int b;
};

enum EnumA { A, B };
enum class EnumB { A, B };

int main()
{
    std::vector<int> vec = { 1, 2, 3 };
    int a = 5;
    float b = 5.5f;
    bool c = true;
    std::string d = "hello";
    int e[10] = { 1, 2, 3 };

    structA strA;
    strA.x = a;
    strA.y = d;

    classA clsA;
    clsA.str = strA;
    clsA.vec = std::vector<int>();
    clsA.vec.push_back(a);

    EnumA enumA = EnumA::A;
    EnumB enumB = EnumB::B;

    unionA uniA;
    uniA.a = 5;

    return 0;
}