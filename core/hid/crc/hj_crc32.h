// g++ hj_crc32.cpp -fPIC -shared -o ../runtime/libcrc.dll

#ifndef HJ_CRC32_H
#define HJ_CRC32_H

// #ifdef __cplusplus
// extern "C"{
// #endif

class HJ_CRC32
{
public:
    HJ_CRC32();
    /*静态成员，c++294页*/
    static unsigned int crc32(char *buf, int len);
    static unsigned int crc32_offset(unsigned char *buf, int len, int offset);
    static unsigned int crc32(unsigned int crc, char* buf, int len);
    static unsigned short crc16(char *ptr, int len, int offset);
};

/*-----------------------------------------------------------------*\
    Python-ctypes对C++的调用，还是基于extern "C"实现的。
    这就意味着，无法调用C++的类对象，也无法调用重载方法或函数。
    以下这种方式，就很蹩脚——相当于重定义了一遍C++的声明……

    -->> 额，虽然函数返回声明为uint，但得到的却是sint（出现了负值） -_-|||

\*-----------------------------------------------------------------*/
#ifdef __cplusplus
extern "C"{
    unsigned int crc32(char *buf, int len){
        return HJ_CRC32::crc32(buf, len);
    }

    unsigned int crc32_offset(unsigned char *buf, int len, int offset){
        return HJ_CRC32::crc32_offset(buf, len, offset);
    }
};
#endif

#endif // HJ_CRC32_H
