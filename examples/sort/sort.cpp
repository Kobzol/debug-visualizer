#include <iostream>
#include <vector>
#include <cstdlib>

template <typename T>
void insertion_sort(std::vector<T>& data)
{
    for (size_t i = 1; i < data.size(); i++)
    {
        T orig = data[i];
        int j = i;
        while (j > 0 && data[j - 1] > orig)
        {
            data[j] = data[j - 1];
            j--;
        }
        data[j] = orig;
    }
}

int main()
{
    srand((unsigned int) time(nullptr));
    std::vector<int> data;

    for (int i = 0; i < 6; i++)
    {
        data.push_back(rand() % 100);
    }

    insertion_sort(data);

    for (size_t i = 0; i < data.size(); i++)
    {
        std::cout << data[i] << " " << std::endl;
    }

    return 0;
}