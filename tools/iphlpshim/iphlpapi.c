/*
 * iphlpapi.dll shim for the ForeverNXT servers (bnetserver.exe, worldserver.exe) under Winlator's Wine.
 *
 * Both servers import exactly one function from iphlpapi, GetAdaptersAddresses, which Trinity::Net::ScanLocalNetworks calls at
 * startup to learn the machine's networks. Wine 10.10's own GetAdaptersAddresses faults inside iphlpapi there (an access violation
 * read at address 9: found with Wine's debugger on the real server, 22 November 2026), and the server then dies in its crash
 * handler. This answers that one call with a single loopback adapter, 127.0.0.1/8, which is all a server that only listens on
 * 127.0.0.1 needs. It is placed in the servers' own folder (never the client's, never the games' system32) and chosen with
 * WINEDLLOVERRIDES="iphlpapi=n,b".
 *
 * Written from the Windows API's documented structures; no Wine or ReactOS code.
 * Build (scripts/build-tools.sh): zig cc -target x86_64-windows-gnu -shared -O2 -s iphlpapi.c -o iphlpapi.dll
 */
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>
#include <string.h>

typedef struct {
	IP_ADAPTER_ADDRESSES adapter;
	IP_ADAPTER_UNICAST_ADDRESS unicast;
	SOCKADDR_IN address;
	char name[40];
	WCHAR friendly[16];
	WCHAR description[40];
} LoopbackBlock;

__declspec(dllexport) ULONG WINAPI GetAdaptersAddresses(ULONG family, ULONG flags, PVOID reserved, PIP_ADAPTER_ADDRESSES out, PULONG size)
{
	(void)flags;
	(void)reserved;
	if (!size) return ERROR_INVALID_PARAMETER;
	/* The loopback adapter is IPv4 only. */
	if (family != AF_UNSPEC && family != AF_INET) return ERROR_NO_DATA;
	if (!out || *size < sizeof(LoopbackBlock)) {
		*size = sizeof(LoopbackBlock);
		return ERROR_BUFFER_OVERFLOW;
	}
	LoopbackBlock *b = (LoopbackBlock *)out;
	memset(b, 0, sizeof(*b));
	strcpy(b->name, "{00000000-0000-0000-0000-000000000001}");
	memcpy(b->friendly, L"Loopback", sizeof(L"Loopback"));
	memcpy(b->description, L"Software Loopback Interface 1", sizeof(L"Software Loopback Interface 1"));

	b->address.sin_family = AF_INET;
	b->address.sin_addr.s_addr = 0x0100007f; /* 127.0.0.1 in network order on a little-endian CPU */

	b->unicast.Length = sizeof(b->unicast);
	b->unicast.Address.lpSockaddr = (LPSOCKADDR)&b->address;
	b->unicast.Address.iSockaddrLength = sizeof(b->address);
	b->unicast.PrefixOrigin = IpPrefixOriginManual;
	b->unicast.SuffixOrigin = IpSuffixOriginManual;
	b->unicast.DadState = IpDadStatePreferred;
	b->unicast.ValidLifetime = 0xffffffff;
	b->unicast.PreferredLifetime = 0xffffffff;
	b->unicast.OnLinkPrefixLength = 8;

	b->adapter.Length = sizeof(b->adapter);
	b->adapter.IfIndex = 1;
	b->adapter.AdapterName = b->name;
	b->adapter.FirstUnicastAddress = &b->unicast;
	b->adapter.FriendlyName = b->friendly;
	b->adapter.Description = b->description;
	b->adapter.Flags = IP_ADAPTER_IPV4_ENABLED;
	b->adapter.Mtu = 65535;
	b->adapter.IfType = IF_TYPE_SOFTWARE_LOOPBACK;
	b->adapter.OperStatus = IfOperStatusUp;
	b->adapter.Ipv4Metric = 75;
	return ERROR_SUCCESS;
}
