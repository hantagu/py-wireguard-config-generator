import subprocess


def generate_keys():
    private_key = subprocess.run('wg genkey', shell=True, capture_output=True).stdout.decode().strip()
    public_key = subprocess.run(f'echo {private_key} | wg pubkey', shell=True, capture_output=True).stdout.decode().strip()
    return public_key, private_key


def generate_psk():
    return subprocess.run('wg genpsk', shell=True, capture_output=True).stdout.decode().strip()


server_ip = input('Server IP: ')
server_port = input('Server port: ')
clients_num = int(input('Number of clients: '))


peers = [{'keys': generate_keys(), 'ip': '10.0.0.1/24'}]
for i in range(2, clients_num+2):
    peers.append({
        'ip': f'10.0.0.{i}/32',
        'psk': generate_psk(),
        'keys': generate_keys()
    })


with open('wg0.conf', 'w') as f:
    f.write('[Interface]\n')
    f.write(f'Address = {peers[0]["ip"]}\n')
    f.write(f'ListenPort = {server_port}\n')
    f.write(f'PrivateKey = {peers[0]["keys"][1]}\n')

    for peer in peers[1:]:
        f.write('\n')
        f.write('[Peer]\n')
        f.write(f'AllowedIPs = {peer["ip"]}\n')
        f.write(f'PublicKey = {peer["keys"][0]}\n')
        f.write(f'PresharedKey = {peer["psk"]}\n')


for i, peer in enumerate(peers[1:]):
    with open(f'wg{i+1}.conf', 'w') as f:
        f.write('[Interface]\n')
        f.write(f'Address = {peer["ip"]}\n')
        f.write(f'PrivateKey = {peer["keys"][1]}\n')
        f.write('\n')
        f.write('[Peer]\n')
        f.write(f'Endpoint = {server_ip}:{server_port}\n')
        f.write(f'PublicKey = {peers[0]["keys"][0]}\n')
        f.write(f'PresharedKey = {peer["psk"]}\n')
        f.write('AllowedIPs = 0.0.0.0/0\n')
        f.write('PersistentKeepalive = 30\n')
