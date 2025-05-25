import socket
import json
import base64
import logging

server_address = ('127.0.0.1', 6666)  # Sesuaikan IP dan port server

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        logging.warning(f"Connecting to {server_address}")

        logging.warning(f"Sending message: {command_str}")
        sock.sendall((command_str + "\r\n\r\n").encode())

        data_received = ""
        while True:
            data = sock.recv(4096)  # baca buffer lebih besar agar efisien
            if not data:
                break
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                break

        try:
            hasil = json.loads(data_received)
            logging.warning("Data received from server:")
            return hasil
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from server response")
            return None
    except Exception as e:
        logging.warning(f"Error during communication: {e}")
        return None
    finally:
        sock.close()

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False
def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False
def remote_upload(filepath=""):
    try:
        # Ekstrak nama file
        filename = filepath.split("/")[-1]

        # Baca isi file dan encode base64
        with open(filepath, "rb") as f:
            encoded_file = base64.b64encode(f.read()).decode()

        # Bangun command string sesuai protokol
        command_str = f"UPLOAD {filename} {encoded_file}"
        hasil = send_command(command_str)

        if hasil['status'] == 'OK':
            print("Upload berhasil")
            return True
        else:
            print("Upload gagal:", hasil['data'])
            return False
    except Exception as e:
        print(f"Error saat upload: {e}")
        return False

def remote_delete(filename=""):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)

    if hasil['status'] == 'OK':
        print("File berhasil dihapus")
        return True
    else:
        print("Gagal menghapus:", hasil['data'])
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    server_address = ('127.0.0.1', 6666)

    while True:
        try:
            cmd = input("Masukkan perintah (LIST, GET <filename>, UPLOAD <filepath>, DELETE <filename>, EXIT): ").strip().split(" ")
            if len(cmd) == 0 or cmd[0] == '':
                continue

            perintah = cmd[0].upper()

            if perintah == "EXIT":
                print("Keluar dari program.")
                break
            elif perintah == "LIST":
                remote_list()
            elif perintah == "GET":
                if len(cmd) < 2:
                    print("[ERROR] Tidak ada nama file yang diberikan!")
                else:
                    remote_get(cmd[1])
            elif perintah == "UPLOAD":
                if len(cmd) < 2:
                    print("[ERROR] Tidak ada path file yang diberikan!")
                else:
                    remote_upload(cmd[1])
            elif perintah == "DELETE":
                if len(cmd) < 2:
                    print("[ERROR] Tidak ada nama file yang diberikan!")
                else:
                    remote_delete(cmd[1])
            else:
                print("[ERROR] Perintah tidak valid!")

        except KeyboardInterrupt:
            print("\nProgram dihentikan oleh user.")
            break
        except Exception as e:
            print(f"[ERROR] Terjadi kesalahan: {e}")