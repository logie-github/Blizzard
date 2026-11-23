#include <winsock2.h>
#include <windows.h>
#include <psapi.h>
#include <wincrypt.h>
#include <stdio.h>
#include <wchar.h>
#include "infinite.h"

static const WCHAR root[] = L"C:\\ForeverNXT-Server";
static const WCHAR ini[] = L"C:\\windows\\blizz-infinite.ini";
static const unsigned short mysql_port = 13306, login_port = 1119, rest_port = 8081;
static unsigned short world_port;

struct service {
    const char *name;
    const WCHAR *log;
    HANDLE process;
    DWORD pid, started;
};

static struct service mysql = {"MySQL", L"C:\\windows\\infinite-mysql.log", NULL, 0, 0};
static struct service login = {"login server", L"C:\\windows\\infinite-login.log", NULL, 0, 0};
static struct service world = {"world server", L"C:\\windows\\infinite-world.log", NULL, 0, 0};
static struct service mysql_admin = {"MySQL shutdown", L"C:\\windows\\infinite-mysql-shutdown.log", NULL, 0, 0};
static WCHAR mysql_admin_exe[MAX_PATH], mysql_admin_config[MAX_PATH];
static HANDLE job;
static BOOL sockets, world_ready;
static DWORD world_checked;
static FILETIME last_crash;
static WCHAR crash_pattern[MAX_PATH + 40];

static BOOL read_path(const WCHAR *key, WCHAR path[MAX_PATH])
{
    DWORD size = GetPrivateProfileStringW(L"Infinite", key, L"", path, MAX_PATH, ini);
    if (size && size < MAX_PATH - 1) return TRUE;
    note("Infinite: missing or oversized path '%ls' in the launch settings", key);
    return FALSE;
}

static BOOL install_ca(const WCHAR *path)
{
    BYTE der[16384];
    DWORD size = 0;
    HANDLE file = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (file == INVALID_HANDLE_VALUE) {
        note("Infinite: could not open the package CA (error %lu)", GetLastError());
        return FALSE;
    }
    BOOL read = ReadFile(file, der, sizeof(der), &size, NULL);
    CloseHandle(file);
    if (!read || !size || size == sizeof(der)) {
        note("Infinite: could not read the package CA");
        return FALSE;
    }

    HCERTSTORE store = CertOpenStore(CERT_STORE_PROV_SYSTEM_W, 0, 0,
                                     CERT_SYSTEM_STORE_LOCAL_MACHINE, L"ROOT");
    BOOL added = store && CertAddEncodedCertificateToStore(store, X509_ASN_ENCODING, der, size,
                                                           CERT_STORE_ADD_USE_EXISTING, NULL);
    if (!added) note("Infinite: could not trust the package CA in Wine (error 0x%08lX)", GetLastError());
    if (store) CertCloseStore(store, 0);
    return added;
}

static BOOL listening(unsigned short port)
{
    struct sockaddr_in address = {0};
    SOCKET fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    BOOL open;
    if (fd == INVALID_SOCKET) return FALSE;
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    open = connect(fd, (const struct sockaddr *)&address, sizeof(address)) == 0;
    closesocket(fd);
    return open;
}

static BOOL running(const struct service *service)
{
    DWORD code = 0;
    if (WaitForSingleObject(service->process, 0) == WAIT_TIMEOUT) return TRUE;
    GetExitCodeProcess(service->process, &code);
    note("Infinite: %s exited (0x%08lX), see %ls", service->name, code, service->log);
    return FALSE;
}

static void ready(const struct service *service, unsigned short port)
{
    PROCESS_MEMORY_COUNTERS memory = {0};
    memory.cb = sizeof(memory);
    GetProcessMemoryInfo(service->process, &memory, sizeof(memory));
    note("Infinite: %s listening on %u after %lu ms, working set %lu MiB", service->name,
         (unsigned int)port, GetTickCount() - service->started, (unsigned long)(memory.WorkingSetSize >> 20));
}

static BOOL wait_for_port(const struct service *service, unsigned short port, DWORD timeout)
{
    DWORD started = GetTickCount();
    while (GetTickCount() - started < timeout) {
        if (infinite_stop_requested()) return FALSE;
        if (!running(service) || (service != &mysql && !running(&mysql))) return FALSE;
        if (listening(port)) {
            ready(service, port);
            return TRUE;
        }
        Sleep(250);
    }
    note("Infinite: timed out waiting for %s on port %u, see %ls", service->name, (unsigned int)port, service->log);
    return FALSE;
}

static BOOL start(struct service *service, const WCHAR *program, WCHAR *command)
{
    SECURITY_ATTRIBUTES inherited = {sizeof(inherited), NULL, TRUE};
    PROCESS_INFORMATION process;
    STARTUPINFOW startup = {0};
    BOOL created;
    DWORD error;

    startup.cb = sizeof(startup);
    startup.dwFlags = STARTF_USESTDHANDLES;
    startup.hStdOutput = CreateFileW(service->log, GENERIC_WRITE, FILE_SHARE_READ, &inherited, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    startup.hStdError = startup.hStdOutput;
    startup.hStdInput = CreateFileW(L"NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, &inherited, OPEN_EXISTING, 0, NULL);
    DWORD flags = CREATE_SUSPENDED | CREATE_NO_WINDOW;
    if (service == &world) {
        // The package uses CTRL_BREAK for shutdown. Give the world server its own hidden console.
        flags = CREATE_SUSPENDED | CREATE_NEW_CONSOLE;
        startup.dwFlags |= STARTF_USESHOWWINDOW;
        startup.wShowWindow = SW_HIDE;
    }
    if (startup.hStdOutput == INVALID_HANDLE_VALUE || startup.hStdInput == INVALID_HANDLE_VALUE) {
        note("Infinite: could not open standard handles for %s (error %lu)", service->name, GetLastError());
        if (startup.hStdOutput != INVALID_HANDLE_VALUE) CloseHandle(startup.hStdOutput);
        if (startup.hStdInput != INVALID_HANDLE_VALUE) CloseHandle(startup.hStdInput);
        return FALSE;
    }
    created = CreateProcessW(program, command, NULL, NULL, TRUE, flags, NULL, root, &startup, &process);
    error = GetLastError();
    CloseHandle(startup.hStdInput);
    CloseHandle(startup.hStdOutput);
    if (!created) {
        note("Infinite: could not start %s (error %lu)", service->name, error);
        return FALSE;
    }
    if (!infinite_add_process(process.hProcess) || ResumeThread(process.hThread) == (DWORD)-1) {
        note("Infinite: could not attach or resume %s (error %lu)", service->name, GetLastError());
        TerminateProcess(process.hProcess, 1);
        CloseHandle(process.hThread);
        CloseHandle(process.hProcess);
        return FALSE;
    }
    CloseHandle(process.hThread);
    service->process = process.hProcess;
    service->pid = process.dwProcessId;
    service->started = GetTickCount();
    note("Infinite: started %s (pid %lu)", service->name, service->pid);
    return TRUE;
}

static FILETIME newest_world_crash(void)
{
    FILETIME latest = {0};
    WIN32_FIND_DATAW entry;
    HANDLE scan = FindFirstFileW(crash_pattern, &entry);
    if (scan == INVALID_HANDLE_VALUE) return latest;
    do {
        if (CompareFileTime(&entry.ftLastWriteTime, &latest) > 0)
            latest = entry.ftLastWriteTime;
    } while (FindNextFileW(scan, &entry));
    FindClose(scan);
    return latest;
}

BOOL infinite_start(void)
{
    WSADATA data;
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION limit = {0};
    WCHAR mysql_exe[MAX_PATH], login_exe[MAX_PATH], world_exe[MAX_PATH];
    WCHAR mysql_config[MAX_PATH], login_config[MAX_PATH], world_config[MAX_PATH], bin[MAX_PATH], ca[MAX_PATH];
    WCHAR command[2 * MAX_PATH + 256], openssl[MAX_PATH + 16];
    int error;

    if (!read_path(L"mysql", mysql_exe) || !read_path(L"mysqlConfig", mysql_config) ||
        !read_path(L"login", login_exe) || !read_path(L"loginConfig", login_config) ||
        !read_path(L"world", world_exe) || !read_path(L"worldConfig", world_config) || !read_path(L"bin", bin) ||
        !read_path(L"ca", ca) || !read_path(L"mysqlAdmin", mysql_admin_exe) ||
        !read_path(L"mysqlAdminConfig", mysql_admin_config))
        return FALSE;

    UINT configured_port = GetPrivateProfileIntW(L"Infinite", L"worldPort", 8085, ini);
    if (!configured_port || configured_port > 65535) {
        note("Infinite: invalid world server port");
        return FALSE;
    }
    world_port = (unsigned short)configured_port;
    if (!install_ca(ca)) return FALSE;

    error = WSAStartup(MAKEWORD(2, 2), &data);
    if (error) {
        note("Infinite: Winsock initialization failed (error %d)", error);
        return FALSE;
    }
    sockets = TRUE;
    const unsigned short ports[] = {mysql_port, login_port, rest_port, world_port};
    for (unsigned int i = 0; i < ARRAYSIZE(ports); i++) {
        if (listening(ports[i])) {
            note("Infinite: a local service is already listening on port %u", (unsigned int)ports[i]);
            return FALSE;
        }
    }
    job = CreateJobObjectW(NULL, NULL);
    limit.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
    if (!job || !SetInformationJobObject(job, JobObjectExtendedLimitInformation, &limit, sizeof(limit))) {
        note("Infinite: could not set up server process cleanup (error %lu)", GetLastError());
        return FALSE;
    }

    swprintf(command, ARRAYSIZE(command), L"\"%ls\" --defaults-file=\"%ls\" --no-monitor --tmpdir=C:/tmp "
             L"--innodb-flush-method=normal --innodb-use-native-aio=OFF --bind-address=127.0.0.1 --console", mysql_exe, mysql_config);
    if (!start(&mysql, mysql_exe, command) || !wait_for_port(&mysql, mysql_port, 120000)) return FALSE;

    swprintf(openssl, ARRAYSIZE(openssl), L"%ls\\openssl.cnf", bin);
    if (!SetEnvironmentVariableW(L"OPENSSL_CONF", openssl) || !SetEnvironmentVariableW(L"OPENSSL_MODULES", bin)) {
        note("Infinite: could not set the server OpenSSL environment (error %lu)", GetLastError());
        return FALSE;
    }
    swprintf(command, ARRAYSIZE(command), L"\"%ls\" -c \"%ls\" --config-dir config\\bnetserver.conf.d", login_exe, login_config);
    if (!start(&login, login_exe, command) || !wait_for_port(&login, login_port, 60000) ||
        !wait_for_port(&login, rest_port, 60000)) return FALSE;

    swprintf(command, ARRAYSIZE(command), L"\"%ls\" -c \"%ls\" --config-dir config\\worldserver.conf.d", world_exe, world_config);
    swprintf(crash_pattern, ARRAYSIZE(crash_pattern), L"%ls\\Crashes\\*worldserver*.dmp", bin);
    last_crash = newest_world_crash();
    BOOL started = start(&world, world_exe, command);
    SetEnvironmentVariableW(L"OPENSSL_CONF", NULL);
    SetEnvironmentVariableW(L"OPENSSL_MODULES", NULL);
    return started;
}

BOOL infinite_stop_requested(void)
{
    return GetFileAttributesW(L"C:\\windows\\blizz-infinite.stop") != INVALID_FILE_ATTRIBUTES;
}

BOOL infinite_poll(void)
{
    DWORD now = GetTickCount();
    if (!running(&mysql) || !running(&login) || !running(&world)) return FALSE;
    if (now - world_checked >= 1000) {
        world_checked = now;
        FILETIME crash = newest_world_crash();
        if (CompareFileTime(&crash, &last_crash) > 0) {
            note("Infinite: the world server wrote a crash dump, see %ls", crash_pattern);
            return FALSE;
        }
        if (!world_ready && listening(world_port)) {
            world_ready = TRUE;
            ready(&world, world_port);
        }
    }
    return TRUE;
}

BOOL infinite_service(DWORD pid)
{
    return pid == mysql.pid || pid == login.pid || pid == world.pid;
}

BOOL infinite_add_process(HANDLE process)
{
    return AssignProcessToJobObject(job, process);
}

static BOOL WINAPI ignore_console_event(DWORD event)
{
    (void)event;
    return TRUE;
}

int infinite_signal_world(DWORD pid)
{
    if (!pid) return 1;
    FreeConsole();
    if (!AttachConsole(pid)) return 1;
    BOOL sent = SetConsoleCtrlHandler(ignore_console_event, TRUE) && GenerateConsoleCtrlEvent(CTRL_BREAK_EVENT, 0);
    if (sent) Sleep(250);
    FreeConsole();
    return sent ? 0 : 1;
}

static BOOL stop_world(void)
{
    // Deliver the console event from a helper so Wine cannot interrupt the keeper's cleanup.
    static const WCHAR keeper[] = L"C:\\windows\\borderless.exe";
    WCHAR command[96];
    PROCESS_INFORMATION helper;
    STARTUPINFOW startup = {0};
    startup.cb = sizeof(startup);
    swprintf(command, ARRAYSIZE(command), L"\"%ls\" /stop-world %lu", keeper, world.pid);
    if (!CreateProcessW(keeper, command, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &startup, &helper)) {
        note("Infinite: could not start the world server shutdown helper (error %lu)", GetLastError());
        return FALSE;
    }
    CloseHandle(helper.hThread);
    BOOL stopped = WaitForSingleObject(world.process, world_ready ? 60000 : 1000) == WAIT_OBJECT_0;
    if (WaitForSingleObject(helper.hProcess, 0) == WAIT_TIMEOUT) TerminateProcess(helper.hProcess, 1);
    CloseHandle(helper.hProcess);
    return stopped;
}

void infinite_stop(void)
{
    if (world.process && WaitForSingleObject(world.process, 0) == WAIT_TIMEOUT) {
        if (stop_world()) {
            note("Infinite: world server stopped");
        } else {
            note("Infinite: world server did not shut down in time");
            TerminateProcess(world.process, 1);
            WaitForSingleObject(world.process, 3000);
        }
    }
    if (login.process && WaitForSingleObject(login.process, 0) == WAIT_TIMEOUT) {
        TerminateProcess(login.process, 0);
        WaitForSingleObject(login.process, 3000);
    }
    if (mysql.process && WaitForSingleObject(mysql.process, 0) == WAIT_TIMEOUT) {
        WCHAR command[2 * MAX_PATH + 80];
        swprintf(command, ARRAYSIZE(command), L"\"%ls\" --defaults-file=\"%ls\" --connect-timeout=5 shutdown",
                 mysql_admin_exe, mysql_admin_config);
        if (start(&mysql_admin, mysql_admin_exe, command) && WaitForSingleObject(mysql.process, 15000) == WAIT_OBJECT_0)
            note("Infinite: MySQL stopped");
        else
            note("Infinite: MySQL shutdown did not finish, closing the server process group");
    }
    if (job) CloseHandle(job);
    if (mysql_admin.process) CloseHandle(mysql_admin.process);
    if (world.process) CloseHandle(world.process);
    if (login.process) CloseHandle(login.process);
    if (mysql.process) CloseHandle(mysql.process);
    if (sockets) WSACleanup();
}
