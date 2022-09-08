#include <iostream>
#include <string>

int main() {
  std::string line;
  int ctr = 3;
  while (std::getline(std::cin, line) && ctr--) {
    std::cout << line << std::endl;
  }
  return 0;
}
