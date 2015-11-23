int test(int a, float d)
{
    int b = a + 1;
    float c = d + a;

    return b + c;
}

int main(int argc, char** argv)
{
    int b = 5;
    b = test(b, 5.0f);

    return 0;
}