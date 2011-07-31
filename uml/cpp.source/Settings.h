#ifndef Settings_h
#define Settings_h

#include <vector>


class Pattern;
class File;

class Settings {

 public:

    virtual void ParseArgs();

 public:
    Boolean Copy;
    Boolean UseCemelot;
    std::vector< String > Searchterms;

 public:

    Pattern *myPattern;


    File ** myFile;
};

#endif // Settings_h
