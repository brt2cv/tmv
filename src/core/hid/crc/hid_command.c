#include "hj_crc32.h"

#define uint unsigned int

typedef struct
{
     unsigned int Header;//0x802e2e80
     unsigned int Crc32; //帧头的crc值
     unsigned short BarCodeLen;
     unsigned char BarCodeType;
     unsigned char ImageType;
     unsigned short ImageWidth;
     unsigned short ImageHeight;
     unsigned int ImageSize;
     unsigned int DecodeTime;//解码时间 ms 作为单位
     unsigned int DataSwitch;//传送数据项开关 24-28
     unsigned int ParaCrc32;//设置参数区的CRC32校验值
     unsigned int ParaAction;//参数设置中需要马上告诉下位机的动作
     unsigned int DeviceID; //设备序列号
     unsigned char BarCodeNum;//条码个数
     unsigned char ScanModeNum;//扫描模式
     unsigned char Rfu[22];   //保留区域,上面大小是42，如果不+保留区会四字节对齐变成44
}T_ProtocolHeaderStu;


/*-----------------------------------------------------------------*\
    Python-ctypes对C++的调用，还是基于extern "C"实现的。
    这就意味着，无法调用C++的类对象，也无法调用重载方法或函数。
    以下这种方式，就很蹩脚——相当于重定义了一遍C++的声明……
\*-----------------------------------------------------------------*/
#ifdef __cplusplus
extern "C"{
#endif

// unsigned int crc32(char *buf, int len){
//     return HJ_CRC32::crc32(buf, len);
// }

// unsigned int crc32_offset(unsigned char *buf, int len, int offset){
//     return HJ_CRC32::crc32_offset(buf, len, offset);
// }

char* make_command(char* head, char* params, uint a, uint b, uint action){
    params[((a) & 0xff00) >> 8] &= (unsigned char)(~((a) & 0x00ff));
    params[((a) & 0xff00) >> 8] |= (unsigned char)(b);

    head[0] = 0x80
    head[1] = 0x2e
    ...

}


#ifdef __cplusplus
};
#endif
