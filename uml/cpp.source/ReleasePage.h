#ifndef ReleasePage_h
#define ReleasePage_h

#include "Release.h"


class ReleasePage : public Release {

 public:

    virtual void FillRelease(Release rel);

 public:
    String Link;

 public:


    /**
     * @element-type Release
     */
    Release *myRelease;
};

#endif // ReleasePage_h
