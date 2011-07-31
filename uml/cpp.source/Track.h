#ifndef Track_h
#define Track_h

#include "File.h"
#include "Pattern.h"

class Release;

class Track : public File, public File {

 public:

    virtual Boolean FilledEnough(Pattern pat);

 public:
    String Artist;
    String Title;
    String Key;
    Integer Number;

 public:

    Release *myRelease;

};

#endif // Track_h
