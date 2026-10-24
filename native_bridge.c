/* Game-thread command bridge for the single verified local build. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <wchar.h>

#define MAGIC 0x5645494e
#define MESSAGE (WM_APP + 0x4a1)
typedef struct {
    uint32_t magic;
    volatile LONG state;
    uint64_t world, pawn;
    uint32_t result, error, thread, reserved;
    WCHAR command[512];
} Request;

static uintptr_t pointer(uintptr_t address) {
    MEMORY_BASIC_INFORMATION page;
    if (!address || !VirtualQuery((void*)address,&page,sizeof(page)) ||
        page.State != MEM_COMMIT || (page.Protect & (PAGE_NOACCESS|PAGE_GUARD)) ||
        address + sizeof(uintptr_t) > (uintptr_t)page.BaseAddress + page.RegionSize) return 0;
    return *(uintptr_t*)address;
}

static int allowed(const WCHAR *command) {
    static const WCHAR *names[]={L"Heal",L"HealEveryone",L"RepairItem",L"LearnEveryRecipe",
        L"LearnEveryBuildObject",L"AddXP",L"SetCondition",L"GiveKey",L"SetTiresPunctured",
        L"Unlock",L"Lockpick",L"SetWeather",L"ClearWeather",L"DiscoverEveryLocation",
        L"RemoveAllCorpses",L"RandomizeTime",L"AddTime",L"TeleportTo",L"SpawnHorde"};
    WCHAR name[64]; unsigned i=0;
    while(command[i] && command[i]!=L' ' && i<63) {name[i]=command[i]; i++;}
    name[i]=0;
    for(unsigned j=0;j<sizeof(names)/sizeof(names[0]);j++) if(!wcscmp(name,names[j])) return 1;
    return 0;
}

static void execute(Request *request) {
    uintptr_t base=(uintptr_t)GetModuleHandleW(NULL);
    IMAGE_DOS_HEADER *dos=(IMAGE_DOS_HEADER*)base;
    IMAGE_NT_HEADERS64 *pe=(IMAGE_NT_HEADERS64*)(base+dos->e_lfanew);
    request->thread=GetCurrentThreadId();
    if (pe->FileHeader.TimeDateStamp!=0x6ad0f986 || pe->OptionalHeader.SizeOfImage!=0xbd5d000) {
        request->error=1; return;
    }
    if (request->thread!=*(DWORD*)(base+0xaf4e108)) {request->error=2;return;}
    uintptr_t world=pointer(base+0xb2186b8);
    if (!world || world!=request->world || pointer(world+56)) {request->error=3;return;}
    uintptr_t gi=pointer(world+552);
    if (!gi || *(int*)(gi+64)!=1) {request->error=3;return;}
    uintptr_t player=pointer(pointer(gi+56));
    uintptr_t controller=pointer(player+48);
    uintptr_t pawn=pointer(controller+768);
    if (!player || !controller || !pawn || pawn!=request->pawn) {request->error=3;return;}
    if (!allowed(request->command)) {request->error=4;return;}
    typedef void* (*GetLog)(void);
    typedef unsigned char (*Exec)(void*,void*,const WCHAR*,void*);
    void *log=((GetLog)(base+0x13c5f20))();
    if (!log) {request->error=5;return;}
    /* ULocalPlayer's FExec base is at +40, verified from the matching PDB. */
    request->result=((Exec)(base+0x4641120))((void*)(player+40),(void*)world,request->command,log);
}

__declspec(dllexport) LRESULT CALLBACK TrainerHook(int code,WPARAM wp,LPARAM lp) {
    if (code>=0 && wp==PM_REMOVE) {
        MSG *msg=(MSG*)lp;
        if (msg->message==MESSAGE && msg->wParam==MAGIC) {
            WCHAR name[80];
            wsprintfW(name,L"Local\\VEINTrainerNative_%lu",GetCurrentProcessId());
            HANDLE mapping=OpenFileMappingW(FILE_MAP_ALL_ACCESS,FALSE,name);
            if (mapping) {
                Request *request=MapViewOfFile(mapping,FILE_MAP_ALL_ACCESS,0,0,sizeof(Request));
                if (request) {
                    if(request->magic==MAGIC && InterlockedCompareExchange(&request->state,2,1)==1) {
                        request->command[511]=0;
                        execute(request);
                        InterlockedExchange(&request->state,3);
                    }
                    UnmapViewOfFile(request);
                }
                CloseHandle(mapping);
            }
            msg->message=WM_NULL;
        }
    }
    return CallNextHookEx(NULL,code,wp,lp);
}

BOOL WINAPI DllMain(HINSTANCE instance,DWORD reason,LPVOID reserved) {
    if(reason==DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(instance);
    return TRUE;
}
