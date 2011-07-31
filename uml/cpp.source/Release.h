#ifndef Release_h
#define Release_h

#include <vector>


class Track;
class ReleasePage;

class Release {

 public:
    String Catid;
    String Name;
    String Type;

 public:

    /**
     * @element-type Track
     */
    Track *myTrack;

    /**
     * @element-type Track
     */
    std::vector< Track* > myTrack;

    /**
     * @element-type ReleasePage
     */
    ReleasePage *myReleasePage;
};

#endif // Release_h
