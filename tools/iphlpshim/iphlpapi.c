/*
 * iphlpapi.dll shim for the ForeverNXT servers (bnetserver.exe, worldserver.exe) under Winlator's Wine.
 *
 * Trinity::Net::ScanLocalNetworks calls GetAdaptersAddresses at startup. Wine 10.10 faults in that call,
 * so the shim supplies one loopback adapter. The client also loads GetAdaptersInfo at runtime.
 * Install the shim beside the server executables and in the Infinite prefix's system32 for the client.
 * Wine selects it with WINEDLLOVERRIDES="iphlpapi=n,b".
 *
 * Written from the Windows API's documented structures; no Wine or ReactOS code.
 * Build (scripts/build-tools.sh): zig cc -target x86_64-windows-gnu -shared -O2 -s iphlpapi.c iphlpapi.def -o iphlpapi.dll
 * (iphlpapi.def lists every name; most are aliases of one stub).
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

ULONG WINAPI GetAdaptersAddresses(ULONG family, ULONG flags, PVOID reserved, PIP_ADAPTER_ADDRESSES out, PULONG size)
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

/* GetAdaptersInfo: the older call, one loopback entry. */
ULONG WINAPI GetAdaptersInfo(PIP_ADAPTER_INFO out, PULONG size)
{
	if (!size) return ERROR_INVALID_PARAMETER;
	if (!out || *size < sizeof(IP_ADAPTER_INFO)) {
		*size = sizeof(IP_ADAPTER_INFO);
		return ERROR_BUFFER_OVERFLOW;
	}
	memset(out, 0, sizeof(*out));
	strcpy(out->AdapterName, "{00000000-0000-0000-0000-000000000001}");
	strcpy(out->Description, "Software Loopback Interface 1");
	out->Index = 1;
	out->Type = MIB_IF_TYPE_LOOPBACK;
	strcpy(out->IpAddressList.IpAddress.String, "127.0.0.1");
	strcpy(out->IpAddressList.IpMask.String, "255.0.0.0");
	return ERROR_SUCCESS;
}

/*
 * Every other name of Wine's iphlpapi (the .def file aliases them) and the compartment calls the client makes by name
 * (SetCurrentThreadCompartmentId: "Failed to load function ... Procedure not found" when missing): answered with a plain result.
 * The client and the servers use the two adapter calls above; the rest of the names are only here so nothing is looked up in vain.
 */
ULONG stub_not_supported(void) { return ERROR_NOT_SUPPORTED; }
ULONG stub_ok(void) { return ERROR_SUCCESS; }
ULONG stub_one(void) { return 1; }
ULONG stub_zero(void) { return 0; }
void *stub_null(void) { return 0; }
