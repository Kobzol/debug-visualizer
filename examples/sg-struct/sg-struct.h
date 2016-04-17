#pragma once

#include <string>

struct Ship
{
public:
    Ship(std::string name, double attack = 0.0);

    double getHealth() const;
    double getAttack() const;
    std::string getName() const;

    void receiveDamage(double amount);

private:
    std::string name;
    double attack;
    double health = 100.0;
};