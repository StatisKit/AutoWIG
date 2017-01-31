#if defined WIN32 || defined _WIN32 || defined __CYGWIN__
    #ifdef LIBBASIC
        #ifdef __GNUC__
            #define BASIC_API __attribute__ ((dllexport))
        #else
            #define BASIC_API __declspec(dllexport)
        #endif
    #else
        #ifdef __GNUC__
            #define BASIC_API __attribute__ ((dllimport))
            #define STATISKIT_LINALG_IMP extern
        #else
            #define BASIC_API __declspec(dllimport)
        #endif
    #endif
#else
    #if __GNUC__ >= 4
        #define BASIC_API __attribute__ ((visibility ("default")))
    #else
        #define BASIC_API
    #endif
#endif