#ifndef ResultPage_h
#define ResultPage_h

#include <vector>


class ReleasePage;

class ResultPage {

 public:

    virtual void Parse();

 public:
    String Link;

 public:

    /**
     * @element-type ReleasePage
     */
    std::vector< ReleasePage* > myReleasePage;
};

#endif // ResultPage_h
