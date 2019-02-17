#!/usr/bin/env python3
import click, socket, time

sock_errors = (
    ValueError,
    socket.error,
    socket.gaierror,
    socket.herror,
    socket.timeout
)

def check_connection( host, port, udp, ipv6, timeout, message ):
    s_settings = {
        'sock_type'  : socket.IPPROTO_UDP if udp else socket.IPPROTO_TCP,
        'addr_family': None,
        'sock_family': None,
        'ip'    : None
    }

    try:
        addr_info = socket.getaddrinfo(
            host,
            port,
            proto=s_settings['sock_type']
        )
    except sock_errors as e:
        return print(e)

    for addr in addr_info:
        af, sf = addr[0], addr[1]
        ip = addr[-1][0]
        if (ipv6 and af == socket.AF_INET6) or (not ipv6 and af == socket.AF_INET):
            s_settings['addr_family'] = af
            s_settings['sock_family'] = sf
            s_settings['ip'] = ip

    if s_settings['addr_family'] == None:
        return

    sock = socket.socket(
        family=s_settings['addr_family'],
        type=s_settings['sock_family'],
        proto=s_settings['sock_type']
    )

    sock.settimeout(timeout)
    result = None
    try:
        if udp:
            sock.sendto(bytes(message, 'utf-8'), ( host, port ))
            result = sock.recv(1024)
            print(result)
        else: result = sock.connect_ex( ( host, port ) )
    except sock_errors as e:
        print(e)
    finally:
        sock.close()

    print({
        'host': host,
        'port': port,
        'up'  : ( result != None ),
        'ip'  : s_settings['ip']
    })

@click.group()
@click.pass_context
@click.option('-h','--host', 'host', type=str,
              required=True, help='host string -- [HOSTNAME|IP]')
@click.option('-p', '--port', type=int, required=True,
              help='port to connect to -- [PORT]')
@click.option('-6', '--ipv6', is_flag=True,
              help='enable IPv6 support for addressing -- default is IPv4')
@click.option('-t', '--timeout', type=int, default=5,
              help='specify timeout for port scan -- default is 5 seconds')
def app( ctx, host, port, ipv6, timeout ):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below
    ctx.ensure_object(dict)

    ctx.obj['host'] = host
    ctx.obj['port'] = port
    ctx.obj['ipv6'] = ipv6
    ctx.obj['timeout'] = timeout
    pass


@app.command()
@click.pass_context
def tcp( ctx ):
    check_connection(
        ctx.obj['host'],
        ctx.obj['port'],
        False,
        ctx.obj['ipv6'],
        ctx.obj['timeout'],
        None
    )

@app.command()
@click.pass_context
@click.option('-uM', '--udp-message', 'udp_message', type=str, required=True,
              help='port to connect to -- [PORT]')
def udp( ctx, udp_message ):
    check_connection(
        ctx.obj['host'],
        ctx.obj['port'],
        True,
        ctx.obj['ipv6'],
        ctx.obj['timeout'],
        udp_message
    )

if __name__ == '__main__':
    cli(obj={})
