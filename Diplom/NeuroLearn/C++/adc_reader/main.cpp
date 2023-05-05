//******************************************************************************
// Модуль E14-440.
// Консольная программа с организацией потокового ввода данных с АЦП
// с одновременной записью получаемых данных на диск в реальном масштабе времени.
// Ввод осуществляется с первых четырёх каналов АЦП на частоте 400 кГц.
//******************************************************************************
#include <stdio.h>
#include <conio.h>
#include <fstream>
#include <string>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <windows.h>
#include <Shlwapi.h>
#include "Lusbapi.h"

#pragma comment(lib, "Shlwapi.lib")

// сохранение сигнала в файл
void SaveSignal(WORD RequestNumber, IO_REQUEST_LUSBAPI* IoReq);
float currentV = 0.0f;

// удаление папки с сигналами
void RecreationDir(const char* directoryPath = "./output");

// аварийный выход из программы
void AbortProgram(char* ErrorString, bool AbortionFlag = true);
// функция потока ввода данных с АЦП
DWORD WINAPI ServiceReadThread(PVOID /*Context*/);
// функция вывода сообщений с ошибками
void ShowThreadErrorMessage(void);

// идентификатор файла
HANDLE hFile;

// идентификатор потока сбора данных
HANDLE hReadThread;
DWORD ReadTid;

// версия библиотеки
DWORD DllVersion;
// указатель на интерфейс модуля
ILE440* pModule;
// дескриптор устройства
HANDLE ModuleHandle;
// название модуля
char ModuleName[7];
// скорость работы шины USB
BYTE UsbSpeed;
// структура с полной информацией о модуле
MODULE_DESCRIPTION_E440 ModuleDescription;
// структура параметров работы АЦП модуля
ADC_PARS_E440 ap;

// кол-во получаемых отсчетов (кратное 32) для Ф. ReadData()
DWORD DataStep = 5024; // * 1024;
// будем собирать NDataBlock блоков по DataStep отсчётов в каждом
const WORD NDataBlock = 80;
// буфер данных
SHORT* ReadBuffer;

// флажок завершения работы потока сбора данных
bool IsReadThreadComplete;
// номер ошибки при выполнении сбора данных
WORD ReadThreadErrorNumber;

// экранный счетчик-индикатор
DWORD Counter = 0x0, OldCounter = 0xFFFFFFFF;

//------------------------------------------------------------------------
// основная программа
//------------------------------------------------------------------------
void main(void)
{
	RecreationDir();

	WORD i;
	//	WORD DacSample;

	// сбросим флажок завершения потока ввода данных
	IsReadThreadComplete = false;
	// пока ничего не выделено под буфер данных
	ReadBuffer = NULL;
	// пока не создан поток ввода данных
	hReadThread = NULL;
	// пока откытого файла нет :(
	hFile = INVALID_HANDLE_VALUE;
	// сбросим флаг ошибок потока ввода данных
	ReadThreadErrorNumber = 0x0;

	// зачистим экран монитора	
	system("cls");

	printf(" *******************************\n");
	printf(" Module E14-440                 \n");
	printf(" Console example for ADC Stream \n");
	printf(" *******************************\n\n");

	// проверим версию используемой библиотеки Lusbapi.dll
	if ((DllVersion = GetDllVersion()) != CURRENT_VERSION_LUSBAPI)
	{
		char String[128];
		printf(String, " Lusbapi.dll Version Error!!!\n   Current: %1u.%1u. Required: %1u.%1u",
			DllVersion >> 0x10, DllVersion & 0xFFFF,
			CURRENT_VERSION_LUSBAPI >> 0x10, CURRENT_VERSION_LUSBAPI & 0xFFFF);

		AbortProgram(String);
	}
	else printf(" Lusbapi.dll Version --> OK\n");

	// попробуем получить указатель на интерфейс
	pModule = static_cast<ILE440*>(CreateLInstance((PCHAR)"e440"));
	if (!pModule) AbortProgram((PCHAR)" Module Interface --> Bad\n");
	else printf(" Module Interface --> OK\n");

	// попробуем обнаружить модуль E14-440 в первых MAX_VIRTUAL_SLOTS_QUANTITY_LUSBAPI виртуальных слотах
	for (i = 0x0; i < MAX_VIRTUAL_SLOTS_QUANTITY_LUSBAPI; i++) if (pModule->OpenLDevice(i)) break;
	// что-нибудь обнаружили?
	if (i == MAX_VIRTUAL_SLOTS_QUANTITY_LUSBAPI) AbortProgram((PCHAR)" Can't find any module E14-440 in first 127 virtual slots!\n");
	else printf(" OpenLDevice(%u) --> OK\n", i);

	// попробуем прочитать дескриптор устройства
	ModuleHandle = pModule->GetModuleHandle();
	if (ModuleHandle == INVALID_HANDLE_VALUE) AbortProgram((PCHAR)" GetModuleHandle() --> Bad\n");
	else printf(" GetModuleHandle() --> OK\n");

	// прочитаем название модуля в обнаруженном виртуальном слоте
	if (!pModule->GetModuleName(ModuleName)) AbortProgram((PCHAR)" GetModuleName() --> Bad\n");
	else printf(" GetModuleName() --> OK\n");
	// проверим, что это 'E14-440'
	if (strcmp(ModuleName, "E440")) AbortProgram((PCHAR)" The module is not 'E14-440'\n");
	else printf(" The module is 'E14-440'\n");

	// попробуем получить скорость работы шины USB
	if (!pModule->GetUsbSpeed(&UsbSpeed)) AbortProgram((PCHAR)" GetUsbSpeed() --> Bad\n");
	else printf(" GetUsbSpeed() --> OK\n");
	// теперь отобразим скорость работы шины USB
	printf("   USB is in %s\n", UsbSpeed ? "High-Speed Mode (480 Mbit/s)" : "Full-Speed Mode (12 Mbit/s)");

	// код LBIOS'а возьмём из соответствующего ресурса штатной DLL библиотеки
	if (!pModule->LOAD_MODULE()) AbortProgram((PCHAR)" LOAD_MODULE() --> Bad\n");
	else printf(" LOAD_MODULE() --> OK\n");

	// проверим загрузку модуля
	if (!pModule->TEST_MODULE()) AbortProgram((PCHAR)" TEST_MODULE() --> Bad\n");
	else printf(" TEST_MODULE() --> OK\n");

	// получим информацию из ППЗУ модуля
	if (!pModule->GET_MODULE_DESCRIPTION(&ModuleDescription)) AbortProgram((PCHAR)" GET_MODULE_DESCRIPTION() --> Bad\n");
	printf(" GET_MODULE_DESCRIPTION() --> OK\n");

	// получим текущие параметры работы АЦП
	if (!pModule->GET_ADC_PARS(&ap)) AbortProgram((PCHAR)" GET_ADC_PARS() --> Bad\n");
	else printf(" GET_ADC_PARS() --> OK\n");

	// установим желаемые параметры работы АЦП
	ap.IsCorrectionEnabled = TRUE;			// разрешим корректировку данных на уровне драйвера DSP
	ap.InputMode = NO_SYNC_E440;				// обычный сбор данных безо всякой синхронизации ввода
	ap.ChannelsQuantity = 0x1;					// число активных каналов
	// формируем управляющую таблицу 
	for (i = 0x0; i < ap.ChannelsQuantity; i++)
		ap.ControlTable[i] = (WORD)(i | (ADC_INPUT_RANGE_10000mV_E440 << 0x6));
	ap.AdcRate = 5.0;							// частота работы АЦП в кГц
	ap.InterKadrDelay = 0.0;					// межкадровая задержка в мс
	ap.AdcFifoBaseAddress = 0x0;			  	// базовый адрес FIFO буфера АЦП в DSP модуля
	ap.AdcFifoLength = MAX_ADC_FIFO_SIZE_E440;	// длина FIFO буфера АЦП в DSP модуля
	// будем использовать фирменные калибровочные коэффициенты, которые храняться в ППЗУ модуля
	for (i = 0x0; i < ADC_CALIBR_COEFS_QUANTITY_E440; i++)
	{
		ap.AdcOffsetCoefs[i] = ModuleDescription.Adc.OffsetCalibration[i];
		ap.AdcScaleCoefs[i] = ModuleDescription.Adc.ScaleCalibration[i];
	}

	// передадим требуемые параметры работы АЦП в модуль
	if (!pModule->SET_ADC_PARS(&ap)) AbortProgram((PCHAR)" SET_ADC_PARS() --> Bad\n");
	else printf(" SET_ADC_PARS() --> OK\n");

	// выделим память под буфер
	ReadBuffer = new SHORT[2 * DataStep];
	if (!ReadBuffer) AbortProgram((PCHAR)" Can not allocate memory\n");

	//// откроем файл для записи получаемых с модуля данных
	//hFile = CreateFile("Test.dat", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
	//	FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN | FILE_FLAG_WRITE_THROUGH, NULL);
	//if (hFile == INVALID_HANDLE_VALUE) AbortProgram((PCHAR)"\n Can't create file 'Test.dat'!\n");

	// Создаём и запускаем поток сбора данных
	printf(" \n");
	hReadThread = CreateThread(0, 0x2000, ServiceReadThread, 0, 0, &ReadTid);
	if (!hReadThread) AbortProgram((PCHAR)" ServiceReadThread() --> Bad\n");
	else printf(" ServiceReadThread() --> OK\n");

	// отобразим параметры сбора данных модуля на экране монитора
	printf(" \n");
	printf(" Module E14-440 (S/N %s) is ready ... \n", ModuleDescription.Module.SerialNumber);
	printf("   Module Info:\n");
	printf("     Module  Revision   is '%c'\n", ModuleDescription.Module.Revision);
	printf("     MCU Driver Version is %s (%s)\n", ModuleDescription.Mcu.Version.Version, ModuleDescription.Mcu.Version.Date);
	printf("     LBIOS   Version    is %s (%s)\n", ModuleDescription.Dsp.Version.Version, ModuleDescription.Dsp.Version.Date);
	printf("   Adc parameters:\n");
	printf("     Data Correction is %s\n", ap.IsCorrectionEnabled ? "enabled" : "disabled");
	printf("     ChannelsQuantity = %2d\n", ap.ChannelsQuantity);
	printf("     AdcRate = %8.3f kHz\n", ap.AdcRate);
	printf("     InterKadrDelay = %2.4f ms\n", ap.InterKadrDelay);
	printf("     KadrRate = %8.3f kHz\n", ap.KadrRate);

	// цикл записи получаемых данных и ожидания окончания работы приложения
//	DacSample = 0x1000;
	printf("\n Press any key if you want to terminate this program...\n\n");
	while (!IsReadThreadComplete)
	{
		if (OldCounter != Counter) 
		{
			printf(" Counter %3u\r", Counter/*, NDataBlock*/); OldCounter = Counter;
		}
		else
		{
			printf("     Current voltage = %2.4f V", currentV);
			Sleep(33);
		}
		//		if(!pModule->ENABLE_TTL_OUT(TRUE)) AbortProgram(" Ошибка разрешения выходных цифровых линий");
		//		if(!pModule->TTL_OUT(0xFFFF)) AbortProgram(" Ошибка установки выходных цифровых линий");
		//		if(!pModule->TTL_OUT(0x0000)) AbortProgram(" Ошибка установки выходных цифровых линий");
		//		if(!pModule->DAC_SAMPLE((SHORT *)&DacSample, 0x0)) AbortProgram(" Ошибка установки канала ЦАП");
	}

	// ждём окончания работы потока ввода данных
	WaitForSingleObject(hReadThread, INFINITE);

	// проверим была ли ошибка выполнения потока сбора данных
	printf("\n\n");
	if (ReadThreadErrorNumber) { AbortProgram(NULL, false); ShowThreadErrorMessage(); }
	/*else AbortProgram(" The program was completed successfully!!!\n", false);*/
}

//------------------------------------------------------------------------
// Поток, в котором осуществляется сбор данных
//------------------------------------------------------------------------
DWORD WINAPI ServiceReadThread(PVOID /*Context*/)
{
	WORD i;
	WORD RequestNumber;
	DWORD FileBytesWritten;
	// массив OVERLAPPED структур из двух элементов
	OVERLAPPED ReadOv[2];
	// массив структур с параметрами запроса на ввод/вывод данных
	IO_REQUEST_LUSBAPI IoReq[2];

	// остановим работу АЦП и одновременно сбросим USB-канал чтения данных
	if (!pModule->STOP_ADC()) { ReadThreadErrorNumber = 0x1; IsReadThreadComplete = true; return 0x0; }

	// формируем необходимые для сбора данных структуры
	for (i = 0x0; i < 0x2; i++)
	{
		// инициализация структуры типа OVERLAPPED
		ZeroMemory(&ReadOv[i], sizeof(OVERLAPPED));
		// создаём событие для асинхронного запроса
		ReadOv[i].hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
		// формируем структуру IoReq
		IoReq[i].Buffer = ReadBuffer + i * DataStep;
		IoReq[i].NumberOfWordsToPass = DataStep;
		IoReq[i].NumberOfWordsPassed = 0x0;
		IoReq[i].Overlapped = &ReadOv[i];
		IoReq[i].TimeOut = (DWORD)(DataStep / ap.AdcRate + 1000);
	}

	// делаем предварительный запрос на ввод данных
	RequestNumber = 0x0;
	if (!pModule->ReadData(&IoReq[RequestNumber])) { CloseHandle(ReadOv[0].hEvent); CloseHandle(ReadOv[1].hEvent); ReadThreadErrorNumber = 0x2; IsReadThreadComplete = true; return 0x0; }

	// запустим АЦП
	if (pModule->START_ADC())
	{
		// цикл сбора данных
		for (i = 0x1; /*i < NDataBlock*/; i++)
		{
			// откроем файл для записи получаемых с модуля данных
			hFile = CreateFile("thread_1.dat", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
				FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN | FILE_FLAG_WRITE_THROUGH, NULL);
			if (hFile == INVALID_HANDLE_VALUE) AbortProgram((PCHAR)"\n Can't create file 'thread_1.dat'!\n");

			// сделаем запрос на очередную порцию данных
			RequestNumber ^= 0x1;
			if (!pModule->ReadData(&IoReq[RequestNumber])) { ReadThreadErrorNumber = 0x2; break; }
			if (ReadThreadErrorNumber) break;

			// ждём завершения операции сбора предыдущей порции данных
			if (WaitForSingleObject(ReadOv[RequestNumber ^ 0x1].hEvent, IoReq[RequestNumber ^ 0x1].TimeOut) == WAIT_TIMEOUT) { ReadThreadErrorNumber = 0x3; break; }
			if (ReadThreadErrorNumber) break;

			//// запишем полученную порцию данных в файл
			//if (!WriteFile(hFile,													// handle to file to write to
			//	IoReq[RequestNumber ^ 0x1].Buffer,					// pointer to data to write to file
			//	2 * DataStep,	 											// number of bytes to write
			//	&FileBytesWritten,									// pointer to number of bytes written
			//	NULL			  											// pointer to structure needed for overlapped I/O
			//)) {
			//	ReadThreadErrorNumber = 0x4; break;
			//}

			SaveSignal(RequestNumber, IoReq);

			if (ReadThreadErrorNumber) break;
			else if (_kbhit()) { ReadThreadErrorNumber = 0x5; break; }
			else Sleep(20);

			// освободим идентификатор файла данных
			if (hFile != INVALID_HANDLE_VALUE) { CloseHandle(hFile); hFile = INVALID_HANDLE_VALUE; }

			Counter++;
		}

		// последняя порция данных
		if (!ReadThreadErrorNumber)
		{
			// откроем файл для записи получаемых с модуля данных
			hFile = CreateFile("thread_1.dat", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
				FILE_ATTRIBUTE_NORMAL | FILE_FLAG_SEQUENTIAL_SCAN | FILE_FLAG_WRITE_THROUGH, NULL);
			if (hFile == INVALID_HANDLE_VALUE) AbortProgram((PCHAR)"\n Can't create file 'Test.dat'!\n");

			RequestNumber ^= 0x1;
			// ждём окончания операции сбора последней порции данных
			if (WaitForSingleObject(ReadOv[RequestNumber ^ 0x1].hEvent, IoReq[RequestNumber ^ 0x1].TimeOut) == WAIT_TIMEOUT) ReadThreadErrorNumber = 0x3;
			//// запишем последнюю порцию данных в файл
			//if (!WriteFile(hFile,													// handle to file to write to
			//	IoReq[RequestNumber ^ 0x1].Buffer,					// pointer to data to write to file
			//	2 * DataStep,	 											// number of bytes to write
			//	&FileBytesWritten,									// pointer to number of bytes written
			//	NULL			  											// pointer to structure needed for overlapped I/O
			//)) ReadThreadErrorNumber = 0x4;

			SaveSignal(RequestNumber, IoReq);

			// освободим идентификатор файла данных
			if (hFile != INVALID_HANDLE_VALUE) { CloseHandle(hFile); hFile = INVALID_HANDLE_VALUE; }

			Counter++;
		}
	}
	else { ReadThreadErrorNumber = 0x6; }

	// остановим работу АЦП
	if (!pModule->STOP_ADC()) ReadThreadErrorNumber = 0x1;
	// прервём возможно незавершённый асинхронный запрос на приём данных
	if (!CancelIo(ModuleHandle)) { ReadThreadErrorNumber = 0x7; }
	// освободим все идентификаторы событий
	for (i = 0x0; i < 0x2; i++) CloseHandle(ReadOv[i].hEvent);
	// небольшая задержка
	Sleep(100);
	// установим флажок завершения работы потока сбора данных
	IsReadThreadComplete = true;
	// теперь можно спокойно выходить из потока
	return 0x0;
}

//------------------------------------------------------------------------
// Отобразим сообщение с ошибкой
//------------------------------------------------------------------------
void ShowThreadErrorMessage(void)
{
	switch (ReadThreadErrorNumber)
	{
	case 0x1:
		printf(" ADC Thread: STOP_ADC() --> Bad\n");
		break;

	case 0x2:
		printf(" ADC Thread: ReadData() --> Bad\n");
		break;

	case 0x3:
		printf(" ADC Thread: Timeout is occured!\n");
		break;

	case 0x4:
		printf(" ADC Thread: Writing data file error!\n");
		break;

	case 0x5:
		// если программа была злобно прервана, предъявим ноту протеста
		printf(" ADC Thread: The program was terminated!\n");
		break;

	case 0x6:
		printf(" ADC Thread: START_ADC() --> Bad\n");
		break;

	case 0x7:
		printf(" ADC Thread: Can't cancel ending input and output (I/O) operations!\n");
		break;

	default:
		printf(" Unknown error!\n");
		break;
	}

	return;
}

void SaveSignal(WORD RequestNumber, IO_REQUEST_LUSBAPI* IoReq)
{
	// Open the output file for writing
	std::ofstream outFile("thread_1.txt");

	DWORD dwNumShorts = 2 * DataStep / sizeof(SHORT);
	// Write each element of the pData array to the file
	for (DWORD i = 0; i < dwNumShorts; i++)
	{
		// Calculating voltage
		auto V = static_cast<float>(IoReq[RequestNumber ^ 0x1].Buffer[i] / pow(2.0f, 13.0f) * 10.0f/* + 0.3227734f*/);
		// Convert the short value to a string and write it to the file
		outFile << std::fixed << std::setprecision(4) << V << std::endl;
		if (i % (DWORD)(dwNumShorts / 30) == 0)
		{
			currentV = V;
		}
	}

	// Close the output file
	outFile.close();


	std::string filename = "./output/thread_" + std::to_string(Counter) + ".txt";
	std::ofstream threadFile(filename);

	// Write each element of the pData array to the file
	for (DWORD i = 0; i < dwNumShorts; i++)
	{
		// Calculating voltage
		auto V = static_cast<float>(IoReq[RequestNumber ^ 0x1].Buffer[i] / pow(2.0f, 13.0f) * 10.0f/* + 0.3227734f*/);
		// Convert the short value to a string and write it to the file
		threadFile << std::fixed << std::setprecision(4) << V << std::endl;
	}

	// Close the output file
	threadFile.close();
}

void RecreationDir(const char* directoryPath)
{
	if (PathIsDirectory(directoryPath)) {
		SHFILEOPSTRUCT file_op = {
		nullptr,
		FO_DELETE,
		directoryPath,
		nullptr,
		FOF_NO_UI,
		FALSE,
		nullptr,
		nullptr
		};
		int result = SHFileOperation(&file_op);
	}

	CreateDirectory(directoryPath, nullptr);
}

//------------------------------------------------------------------------
// аварийное завершение программы
//------------------------------------------------------------------------
void AbortProgram(char* ErrorString, bool AbortionFlag)
{
	// подчищаем интерфейс модуля
	if (pModule)
	{
		// освободим интерфейс модуля
		if (!pModule->ReleaseLInstance()) printf(" ReleaseLInstance() --> Bad\n");
		else printf(" ReleaseLInstance() --> OK\n");
		// обнулим указатель на интерфейс модуля
		pModule = NULL;
	}

	// освободим память буфера
	if (ReadBuffer) { delete[] ReadBuffer; ReadBuffer = NULL; }
	// освободим идентификатор потока сбора данных
	if (hReadThread) { CloseHandle(hReadThread); hReadThread = NULL; }
	// освободим идентификатор файла данных
	if (hFile != INVALID_HANDLE_VALUE) { CloseHandle(hFile); hFile = INVALID_HANDLE_VALUE; }

	// выводим текст сообщения
	if (ErrorString) printf(ErrorString);

	// прочистим очередь клавиатуры
	if (_kbhit()) { while (_kbhit()) _getch(); }

	// если нужно - аварийно завершаем программу
	if (AbortionFlag) exit(0x1);
	// или спокойно выходим из функции   
	else return;
}

