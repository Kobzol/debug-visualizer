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

int main()
{
    std::vector<int> vec = { 1, 2, 3 };
    int a = 5;
    float b = 5.5f;
    bool c = true;
    std::string d = "hello";

    structA strA;
    strA.x = a;
    strA.y = d;

    classA clsA;
    clsA.str = strA;
    clsA.vec = std::vector<int>();
    clsA.vec.push_back(a);

    return 0;
}