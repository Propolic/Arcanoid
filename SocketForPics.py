import socket
import struct

# класс дял получения картинки размером в указанное число байт (число абйт ставим каждый раз перед картинкой и заканчиваем двоеточием:
class Socket4Pics():
    def __init__(self, sock):
        self._sock = sock
        pass

    def send_msg(self, msg):
        # Каждое сообщение будет иметь префикс в 4 байта блинной(network byte order)
        k = struct.pack('>I', len(msg))
        self._sock.send(k) # отправляем длину сообщения
        self._sock.send(msg) # отправляем само сообщение

    def send_msg_end(self, msg = "0"):
        # Каждое сообщение будет иметь префикс в 4 байта блинной(network byte order)
        datagram = msg.encode() # кодируем
        print("Функция отправки 0 клиенту в байтах: " + str(datagram))
        self._sock.send(datagram) # отправляем сообщения об окончании сессии


    def recv_msg_floats(self):
        # Получение длины сообщения и распаковка в integer
        raw_msglen = self.recvall(4)
        if raw_msglen == b'0': # получено сообщение о прекращении сеанса
            return b'0'
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Получение данных
        return self.recvall_floats(msglen)

    def recvall_floats(self, n):
        # Функция для получения n байт или возврата None если получен EOF
        data = ''
        while len(data) <= n:
            packet = self._sock.recv(n - len(data))
            if packet == b'0': # получено сообщение о прекращении сеанса
                return -1
            if not packet:
                return None
            data += packet
        return data


    def recv_msg(self):
        # Получение длины сообщения и распаковка в integer
        raw_msglen = self.recvall(4)
        if raw_msglen == b'0': # получено сообщение о прекращении сеанса
            return b'0'
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Получение данных
        return self.recvall(msglen)

    def recvall(self, n):
        # Функция для получения n байт или возврата None если получен EOF
        data = b''
        while len(data) < n:
            packet = self._sock.recv(n - len(data))
            if packet == b'0': # получено сообщение о прекращении сеанса
                return b'0'
            if not packet:
                return None
            data += packet
        return data
    '''
    def recvall_wo_cnt_bytes(self, data):
        len_cnt_bytes_str = data.index(':')
        data = data[len_cnt_bytes_str:]
        return data
    '''

def main():
    pass

if __name__ == '__main__':
    main()
