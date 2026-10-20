/* SacredFire: runtime_net.c against local listeners (docs/sacredfire/15-online.md). Includes the
 * source to reach its contracts directly; nothing here leaves the machine (127.0.0.1 only). */
#include "../src/runtime_net.c"
#include <assert.h>

uintptr_t runtime_lookup(const RuntimeExport *table,size_t count,const char *nid) {
    for (size_t i=0;i<count;++i) if (!strcmp(table[i].name,nid)) return (uintptr_t)table[i].function;
    return 0;
}

static int32_t guest_errno;
int32_t *runtime_errno(void) { return &guest_errno; }
const char *runtime_symbol(const char *nid) { return nid; } /* the tests name imports by symbol */

static NativeSocket listen_on(uint16_t *port, int type) {
    NativeSocket s=socket(AF_INET,type,0);
    assert(s!=NATIVE_INVALID);
    struct sockaddr_in a={0};
    a.sin_family=AF_INET; a.sin_addr.s_addr=htonl(0x7f000001);
    assert(!bind(s,(struct sockaddr *)&a,sizeof a));
    socklen_t len=sizeof a;
    assert(!getsockname(s,(struct sockaddr *)&a,&len));
    *port=ntohs(a.sin_port);
    if (type==SOCK_STREAM) assert(!listen(s,4));
    return s;
}
static PsSockaddrIn guest_addr(const char *ip, uint16_t port) {
    PsSockaddrIn a;
    memset(&a,0,sizeof a);
    a.len=sizeof a; a.family=PS_AF_INET; a.port=htons(port);
    assert(parse_ipv4(ip,&a.addr));
    return a;
}

/* A one-request HTTP server: answers chunked, keeps what it received. */
static char http_seen[4096];
static const char *http_reply="HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nTransfer-Encoding: chunked\r\n\r\n"
                              "5\r\n{\"ok\"\r\n6\r\n:true}\r\n0\r\n\r\n";
static void *http_server(void *arg) {
    NativeSocket listener=*(NativeSocket *)arg;
    NativeSocket c=accept(listener,NULL,NULL);
    size_t got=0;
    while (got<sizeof http_seen-1) {
        const int k=recv(c,http_seen+got,(int)(sizeof http_seen-1-got),0);
        if (k<=0) break;
        got+=(size_t)k; http_seen[got]=0;
        const char *end=strstr(http_seen,"\r\n\r\n");
        if (end && (strstr(http_seen,"\r\n\r\nping") || !strstr(http_seen,"Content-Length"))) break;
    }
    memset(http_seen+got,0,sizeof http_seen-got);
    send(c,http_reply,(int)strlen(http_reply),0);
    native_close(c);
    return NULL;
}

static int netctl_events, np_events;
static void ABI on_netctl(int event,void *arg) { assert(event==3 && arg==&netctl_events); ++netctl_events; }
static void ABI on_np(int32_t user,int32_t state,void *arg) { assert(user==1 && state==2 && arg==&np_events); ++np_events; }

int main(int argc,char **argv) {
    if (argc>1 && !strcmp(argv[1],"--offline")) {           /* no server: nothing is answered */
        unsetenv("BB_ONLINE_SERVER");
        assert(!runtime_net_resolve("sceNetSocket") && !runtime_net_resolve("sceNpGetState"));
        puts("net-test: offline ok");
        return 0;
    }
    setenv("BB_USER_NAME","Sergio Test",1);
    uint16_t http_port;
    NativeSocket http_listener=listen_on(&http_port,SOCK_STREAM);
    char port_text[16];
    snprintf(port_text,sizeof port_text,"%u",http_port);
    setenv("BB_ONLINE_HTTP_PORT",port_text,1);
    setenv("BB_ONLINE_SERVER","127.0.0.1",1);
    assert(runtime_net_resolve("sceNetSocket")==(uintptr_t)net_socket);
    assert(!strcmp(cfg.online_id,"Sergio_Test") && cfg.account_id);

    /* Every name answers the private server; literals stay literals. */
    const int resolver=net_resolver_create("dw",0,0);
    uint32_t addr=0;
    assert(!net_resolver_ntoa(resolver,"lavender-ps4-auth3.prod.demonware.net",&addr,0,0,0));
    assert(addr==htonl(0x7f000001));
    assert(!net_resolver_ntoa(resolver,"10.1.2.3",&addr,0,0,0) && addr==htonl(0x0a010203));

    /* TCP through epoll, both ways. */
    uint16_t port;
    NativeSocket listener=listen_on(&port,SOCK_STREAM);
    const int s=net_socket("dw_lobby",PS_AF_INET,PS_SOCK_STREAM,0);
    assert(s>0);
    PsSockaddrIn to=guest_addr("127.0.0.1",port);
    assert(!net_connect(s,&to,sizeof to));
    NativeSocket peer=accept(listener,NULL,NULL);
    assert(peer!=NATIVE_INVALID);
    assert(net_send(s,"hello",5,0)==5);
    char buffer[64]={0};
    assert(recv(peer,buffer,sizeof buffer,0)==5 && !memcmp(buffer,"hello",5));
    const int ep=net_epoll_create("dw",0);
    PsEpollEvent watch={PS_EPOLLIN,0,0,0x1234};
    assert(!net_epoll_control(ep,1,s,&watch));
    PsEpollEvent events[4];
    assert(net_epoll_wait(ep,events,4,1000)==0);           /* nothing to read yet: 1 ms */
    assert(net_recv(s,buffer,sizeof buffer,PS_MSG_DONTWAIT)==NET_ERROR(E_AGAIN) && net_errno==E_AGAIN);
    send(peer,"world!",6,0);
    assert(net_epoll_wait(ep,events,4,2000000)==1);
    assert(events[0].ident==(uint64_t)s && (events[0].events & PS_EPOLLIN) && events[0].data==0x1234);
    assert(net_recv(s,buffer,sizeof buffer,0)==6 && !memcmp(buffer,"world!",6));
    PsSockaddrIn me;
    uint32_t me_len=sizeof me;
    assert(!net_getsockname(s,&me,&me_len) && me.family==PS_AF_INET && me_len==16);
    assert(!net_epoll_control(ep,3,s,NULL));
    assert(!net_socket_close(s));
    native_close(peer); native_close(listener);

    /* UDP. */
    uint16_t udp_port;
    NativeSocket udp=listen_on(&udp_port,SOCK_DGRAM);
    const int u=net_socket("dw_nat",PS_AF_INET,PS_SOCK_DGRAM_P2P,0);
    PsSockaddrIn udp_to=guest_addr("127.0.0.1",udp_port);
    assert(net_sendto(u,"nat?",4,0,&udp_to,sizeof udp_to)==4);
    struct sockaddr_in from;
    socklen_t from_len=sizeof from;
    assert(recvfrom(udp,buffer,sizeof buffer,0,(struct sockaddr *)&from,&from_len)==4);
    sendto(udp,"nat!",4,0,(struct sockaddr *)&from,from_len);
    PsSockaddrIn source;
    uint32_t source_len=sizeof source;
    assert(net_recvfrom(u,buffer,sizeof buffer,0,&source,&source_len)==4 && !memcmp(buffer,"nat!",4));
    assert(source.port==htons(udp_port) && source.addr==htonl(0x7f000001));
    int nbio=1;
    assert(!net_setsockopt(u,PS_SOL_SOCKET,0x1200,&nbio,4));
    assert(net_recvfrom(u,buffer,sizeof buffer,0,NULL,NULL)==NET_ERROR(E_AGAIN));
    int type=0;
    uint32_t type_len=4;
    assert(!net_getsockopt(u,PS_SOL_SOCKET,0x1008,&type,&type_len) && type==PS_SOCK_DGRAM_P2P);
    native_close(udp);

    /* Nothing but the private server is reachable. */
    PsSockaddrIn outside=guest_addr("8.8.8.8",53);
    const int t=net_socket("outside",PS_AF_INET,PS_SOCK_STREAM,0);
    assert(net_connect(t,&outside,sizeof outside)==NET_ERROR(E_NETUNREACH));
    assert(net_sendto(u,"x",1,0,&outside,sizeof outside)==NET_ERROR(E_HOSTUNREACH));
    net_socket_close(t); net_socket_close(u);

    /* HTTPS becomes plain HTTP to the private server's HTTP port, chunked replies decoded. */
    pthread_t server;
    pthread_create(&server,NULL,http_server,&http_listener);
    const int tmpl=http_template(1,"CTR/1.0",1,0);
    assert(!http_add_header(tmpl,"X-Title","CUSA13795",0));
    const int conn=http_connection(tmpl,"https://lavender-ps4-auth3.prod.demonware.net:443",1);
    const int req=http_request2(conn,"POST","https://lavender-ps4-auth3.prod.demonware.net/v1/auth?x=1",4);
    int status=0;
    assert(http_status(req,&status)==HTTP_BEFORE_SEND);
    assert(!http_send(req,"ping",4));
    pthread_join(server,NULL);
    assert(strstr(http_seen,"POST /v1/auth?x=1 HTTP/1.1\r\n"));
    assert(strstr(http_seen,"Host: lavender-ps4-auth3.prod.demonware.net\r\n"));
    assert(strstr(http_seen,"X-SacredFire-Scheme: https\r\n") && strstr(http_seen,"X-Title: CUSA13795\r\n"));
    assert(strstr(http_seen,"User-Agent: CTR/1.0\r\n") && strstr(http_seen,"Content-Length: 4\r\n"));
    assert(!http_status(req,&status) && status==200);
    int exists=-1;
    uint64_t length=0;
    assert(!http_response_length(req,&exists,&length) && !exists && length==11);
    char body[32]={0};
    assert(http_read(req,body,4)==4 && http_read(req,body+4,sizeof body)==7 && !strcmp(body,"{\"ok\":true}"));
    assert(http_read(req,body,sizeof body)==0);
    char *headers;
    uint64_t headers_size;
    assert(!http_all_headers(req,&headers,&headers_size));
    const char *value;
    uint64_t value_size;
    assert(!http_parse_header(headers,headers_size,"content-type",&value,&value_size));
    assert(value_size==16 && !memcmp(value,"application/json",16));
    assert(http_parse_header(headers,headers_size,"X-Missing",&value,&value_size)==HTTP_PARSE_NOT_FOUND);
    char escaped[32];
    uint64_t need=0;
    assert(!http_uri_escape(escaped,&need,sizeof escaped,"a b/c") && !strcmp(escaped,"a%20b%2Fc") && need==10);
    assert(!http_delete(req) && !http_delete(conn) && !http_delete(tmpl));

    /* NpWebApi: PSN services as HTTPS to the private server; errors as 0x82f00000 | status. */
    http_reply="HTTP/1.1 404 Not Found\r\nX-Np-Error: 1\r\nContent-Length: 13\r\n\r\n{\"error\":404}";
    pthread_create(&server,NULL,http_server,&http_listener);
    const int lib=webapi_init(1,0);
    const int user_ctx=webapi_create_context_a(lib,1);
    assert(user_ctx>0 && webapi_create_context_a(lib,2)==WEBAPI_NOT_SIGNED_IN);
    int64_t web=0;
    assert(!webapi_create_request(user_ctx,"userProfile","/v1/users/me/friendList",0,NULL,&web) && web>0);
    assert(!webapi_add_header(web,"Accept-Language","es"));
    char error[64];
    WebApiResponseInfo info={0,error,sizeof error,0};
    assert(webapi_send2(web,NULL,0,&info)==(int32_t)0x82f00194);
    pthread_join(server,NULL);
    assert(strstr(http_seen,"GET /v1/users/me/friendList HTTP/1.1\r\nHost: userProfile.np.community.playstation.net\r\n"));
    assert(strstr(http_seen,"Accept-Language: es\r\n"));
    assert(info.status==404 && info.data_size==13 && !strcmp(error,"{\"error\":404}"));
    uint64_t header_length=0;
    char header_value[8];
    assert(!webapi_header_length(web,"X-Np-Error",&header_length) && header_length==1);
    assert(!webapi_header_value(web,"x-np-error",header_value,sizeof header_value) && !strcmp(header_value,"1"));
    assert(!webapi_delete_request(web) && webapi_delete_request(web)==WEBAPI_REQUEST_NOT_FOUND);
    NpId parsed;
    assert(!webapi_parse_npid("U2VyZ2lvQGIxLmV1",&parsed) && !strcmp(parsed.handle.data,"Sergio")); /* Sergio@b1.eu */
    native_close(http_listener);

    /* NetCtl and PSN: connected, user 1 signed in, each callback told once. */
    int32_t state=0, cid=-1;
    assert(!netctl_state(&state) && state==3);
    assert(!netctl_register_toolkit((void *)on_netctl,&netctl_events,&cid));
    netctl_check_toolkit(); netctl_check_toolkit();
    assert(netctl_events==1);
    char ip[256];
    assert(!netctl_info(14,ip) && !strcmp(ip,"127.0.0.1"));
    assert(!np_state(1,&state) && state==2);
    assert(!np_state(2,&state) && state==1);
    NpOnlineId id;
    assert(!np_online_id(1,&id) && !strcmp(id.data,"Sergio_Test"));
    assert(np_online_id(2,&id)==NP_SIGNED_OUT);
    assert(!np_register_toolkit((void *)on_np,&np_events));
    np_check_callback(); np_check_callback();
    assert(np_events==1);
    const int32_t auth=np_create_async(NULL);
    NpAuthCodeParameterA param={32,1,{0},"client-id","psn:s2s"};
    char code[136];
    int32_t issuer=0, result=-1;
    assert(!np_auth_code_a(auth,&param,code,&issuer) && issuer==256 && !strncmp(code,"SACREDFIRE-Sergio_Test-",23));
    assert(!np_poll(auth,&result) && result==0);
    assert(!np_delete_request(auth));
    NpCheckPlusParameter plus={sizeof plus,1,{0},1,{0}};
    unsigned char granted[33];
    const int32_t sync=np_create_request();
    assert(!np_check_plus(sync,&plus,granted) && granted[0]==1);
    /* POSIX sockets: -1 and errno; PSN services not offered yet fail softly, cleanups succeed. */
    const int ps=posix_socket(PS_AF_INET,PS_SOCK_STREAM,0);
    assert(ps>0);
    assert(posix_connect(ps,&outside,sizeof outside)==-1 && guest_errno==E_NETUNREACH);
    GuestFdSet readable={{0}};
    readable.bits[0]=1ull<<ps;
    GuestTimeval none={0,0};
    assert(posix_select(ps+1,&readable,NULL,NULL,&none)>=0);
    net_socket_close(ps);
    typedef int32_t (ABI *Call)(void);
    Call tus=(Call)runtime_net_resolve("sceNpTusCreateNpTitleCtxA#libSceNpTus");
    assert(tus && tus()==(int32_t)0x80550809);
    Call tus_delete=(Call)runtime_net_resolve("sceNpTusDeleteNpTitleCtx#libSceNpTus");
    assert(tus_delete && !tus_delete());
    assert(!runtime_net_resolve("sceKernelFoo#libkernel"));
    puts("net-test: ok");
    return 0;
}
