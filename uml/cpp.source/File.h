#ifndef File_h
#define File_h

#include "Pattern.h"
#include "TagHeader.h"


class File : public TagHeader {

 public:

    virtual void Rename(Pattern pat);

    virtual String GetSuffix();

    virtual void Copy(Pattern pat);

 public:
    String Path;
    String Type;

 public:


    TagHeader *myTagHeader;
};

#endif // File_h
