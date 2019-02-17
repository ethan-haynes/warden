#!/usr/bin/env python3
import click, socket, time

sock_errors = (
    ValueError,
    socket.error,
    socket.gaierror,
    socket.herror,
    socket.timeout
)

def check_connection( host, port, udp, ipv6 ):
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

    try:
        result = sock.connect_ex( ( host, port ) )
        print(result)
    except sock_errors as e:
        return print(e)

    sock.close()
    print({
        'host': host,
        'port': port,
        'up'  : ( result == 0 ),
        'ip'  : s_settings['ip']
    })

@click.command()
@click.option('-h','--host', 'host', type=str,
              required=True, help='host string -- [HOSTNAME|IP]')
@click.option('-p', '--port', type=int, required=True,
              help='port to connect to -- [PORT]')
@click.option('--udp', is_flag=True,
              help='enable udp for protocol')
@click.option('-6', '--ipv6', is_flag=True,
              help='enable IPv6 support for addressing')
def app( host, port, udp, ipv6 ):
    """Simple program that checks port on given host."""
    check_connection( host, port, udp, ipv6 )

if __name__ == '__main__':
    app()
