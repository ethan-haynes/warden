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
    s_settings = dict(
        sock_type=socket.IPPROTO_UDP if udp else socket.IPPROTO_TCP,
        addr_family=None,
        sock_family=None,
        address=None,
        result=None,
        reason=None
    )

    try:
        addr_info = socket.getaddrinfo(
            host,
            port,
            proto=s_settings['sock_type']
        )
    except sock_errors as e:
        return print({ 'error': str(e) })

    for addr in addr_info:
        af, sf = addr[0], addr[1]
        address = addr[-1]
        if (ipv6 and af == socket.AF_INET6) or (not ipv6 and af == socket.AF_INET):
            s_settings['addr_family'] = af
            s_settings['sock_family'] = sf
            s_settings['address'] = address


    if s_settings['addr_family'] == None:
        return print({
            'error': f'address family for host {host} does not match provided type of { "IPv6" if ipv6 else "IPv4"}'
        })

    sock = socket.socket(
        family=socket.AF_INET,
        type=s_settings['sock_family'],
        proto=s_settings['sock_type']
    )

    sock.settimeout(timeout)
    try:
        if udp:
            sock.sendto(bytes(message, 'utf-8'), address)
            s_settings['result'] = sock.recv(1024)
        else:
            s_settings['result'] = sock.connect_ex( address )
    except sock_errors as e:
        s_settings['reason'] = str(e)
    finally:
        sock.close()

    out = {
        'host': host,
        'port': port,
        'up'  : ( s_settings['result'] != None if udp else  s_settings['result'] == 0 ),
        'ip'  : s_settings['address'][0]
    }
    if s_settings['reason'] != None:
        out['reason'] = s_settings['reason'] # adding failure reason

    print(out)

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
