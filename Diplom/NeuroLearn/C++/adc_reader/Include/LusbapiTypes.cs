// Generated using CppHeader2CS
#define __LusbapiTypesH__

using System;
using System.Runtime.InteropServices;


namespace C2CS
{
#if ! __LusbapiTypesH__
#if ! NAME_LINE_LENGTH_LUSBAPI
#endif
#if ! SERIAL_NUMBER_STRING_LENGTH_LUSBAPI
#endif
#if ! COMMENT_LINE_LENGTH_LUSBAPI
#endif
#if ! ADC_CALIBR_COEFS_QUANTITY_LUSBAPI
#endif
#if ! DAC_CALIBR_COEFS_QUANTITY_LUSBAPI
#endif
    public struct IO_REQUEST_LUSBAPI
    {
    } 

    public struct LAST_ERROR_INFO_LUSBAPI
    {
    } 

    public struct VERSION_INFO_LUSBAPI
    {
    } 

    public struct MCU_VERSION_INFO_LUSBAPI
    {
        public VERSION_INFO_LUSBAPI FwVersion;						// ���������� � ������ �������� �������� ��������� '����������'(Application) ����������������
        public VERSION_INFO_LUSBAPI BlVersion;						// ���������� � ������ �������� '����������'(BootLoader) ����������������
    } 

    public struct MODULE_INFO_LUSBAPI
    {
    } 

    public struct DSP_INFO_LUSBAPI
    {
        public double ClockRate;										// �������� ������� ������ DSP � ���
        public VERSION_INFO_LUSBAPI Version;							// ���������� � �������� DSP
    } 

    public struct MCU_INFO_LUSBAPI
    {
        public double ClockRate;										// �������� ������� ������ ���������������� � ���
        public VERSION_INFO_LUSBAPI Version;							// ���������� � ������ �������� ����������������
    } 

    public struct ADC_INFO_LUSBAPI
    {
        public double OffsetCalibration[ADC_CALIBR_COEFS_QUANTITY_LUSBAPI];	// ���������������� ������������ �������� ����
        public double ScaleCalibration[ADC_CALIBR_COEFS_QUANTITY_LUSBAPI];		// ���������������� ������������ ��������
    } 

    public struct DAC_INFO_LUSBAPI
    {
        public double OffsetCalibration[DAC_CALIBR_COEFS_QUANTITY_LUSBAPI];	// ���������������� ������������
        public double ScaleCalibration[DAC_CALIBR_COEFS_QUANTITY_LUSBAPI];		// ���������������� ������������
    } 

    public struct DIGITAL_IO_INFO_LUSBAPI
    {
    } 

    public struct INTERFACE_INFO_LUSBAPI
    {
    } 

#endif
    class Constants
    {
#if ! __LusbapiTypesH__
#if ! NAME_LINE_LENGTH_LUSBAPI
        public const int NAME_LINE_LENGTH_LUSBAPI = 25; 
#endif
#if ! SERIAL_NUMBER_STRING_LENGTH_LUSBAPI
        public const int SERIAL_NUMBER_STRING_LENGTH_LUSBAPI = 16; 
#endif
#if ! COMMENT_LINE_LENGTH_LUSBAPI
        public const int COMMENT_LINE_LENGTH_LUSBAPI = 256; 
#endif
#if ! ADC_CALIBR_COEFS_QUANTITY_LUSBAPI
        public const int ADC_CALIBR_COEFS_QUANTITY_LUSBAPI = 128; 
#endif
#if ! DAC_CALIBR_COEFS_QUANTITY_LUSBAPI
        public const int DAC_CALIBR_COEFS_QUANTITY_LUSBAPI = 128; 
#endif
#endif
    }
}
