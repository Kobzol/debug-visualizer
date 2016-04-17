#include <iostream>
#include <random>
#include <ctime>

#include "sg-struct.h"

Ship::Ship(std::string name, double attack) : name(name), attack(attack)
{

}

double Ship::getHealth() const
{
    return this->health;
}
double Ship::getAttack() const
{
    return this->attack;
}
std::string Ship::getName() const
{
    return this->name;
}

void Ship::receiveDamage(double amount)
{
    this->health -= amount;
}

std::default_random_engine generator((unsigned int) time(nullptr));
std::uniform_int_distribution<int> distribution(2, 8);

int main()
{
    Ship sg1("O'Neill-class ship", 8.0);
    Ship ori("Ori warship", 10.0);
    Ship* ships[2] = { &sg1, &ori };

    while (sg1.getHealth() > 0.0 && ori.getHealth() > 0.0)
    {
        for (int i = 0; i < 2; i++)
        {
            int value = distribution(generator);

            if (i == 0 && distribution(generator) > 6)
            {
                value /= 2.0;
            }

            int target = 1 - i;
            double damage = ships[i]->getAttack() * (1.0 / value);
            ships[target]->receiveDamage(damage);
            std::cout   << ships[target]->getName() << " received "
                        << damage << " damage from "
                        << ships[i]->getName() << std::endl;
        }
    }

    int winner = 0;
    if (ships[1]->getHealth() > ships[0]->getHealth())
    {
        winner = 1;
    }

    std::cout << "The winner is " << ships[winner]->getName() << std::endl;

    return 0;
}