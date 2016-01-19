#include "hello_world.h"

World::World()
{ msg = "hello"; }

const std::string& World::great() const
{ return msg; }

void World::set(const std::string& msg)
{ this->msg = msg; }
