import time
from django.shortcuts import render
import threading
from queue import Queue
import cv2
import socket
import struct
import io
import numpy as np
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required

from accounts.models import Communication


FLAG = True

def socket_connect(socket, ip, port):
            while True:
                try:
                    socket.connect((ip, port))
                    break
                except Exception as e:
                    print(e)


# class VideoCamera():
#     def __init__(self, fq, ip, port):
#         self.fq = fq

#         self.client_socket = socket.socket()
#         self.ip = ip
#         self.port = port
#         socket_connect(self.client_socket, self.ip, self.port)

#         self.connection = self.client_socket.makefile('rb')

#         threading.Thread(target=self.get_frame, args=()).start()

#     def __del__(self):
#         self.connection.close()

#     def get_frame(self):
#         while True:
#             try:
#                 byte_res = self.connection.read(struct.calcsize('<L'))
#                 image_len = struct.unpack('<L', byte_res)[0]
#             except:
#                 if len(byte_res) == 0:
#                     socket_connect(self.client_socket, self.ip, self.port)
                
#             image_stream = io.BytesIO()
#             image_stream.write(self.connection.read(image_len))

#             image_stream.seek(0)
#             image_np = np.frombuffer(image_stream.getvalue(), dtype=np.uint8)
#             image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

#             while self.fq.qsize() > 1:
#                 self.fq.get()
#             # print(self.frame)
#             self.fq.put(image)
                    
class VideoCamera():
    def __init__(self, fq, ip, port):
        self.fq = fq
        self.ip = ip
        self.port = port
        self.reconnect_delay = 5  # Set the initial reconnect delay to 5 seconds

        self.connect()  # Call the connect method to establish the initial connection

        threading.Thread(target=self.get_frame, args=()).start()

    def connect(self):
        connected = False
        for _ in range(10):
            if connected:
                break
            try:
                self.client_socket = socket.socket()
                self.client_socket.connect((self.ip, self.port))
                self.connection = self.client_socket.makefile('rb')
                connected = True
                break
            except:
                time.sleep(2)

    def __del__(self):
        self.connection.close()
        self.client_socket.close()

    def get_frame(self):
        while True:
            try:
                byte_res = self.connection.read(struct.calcsize('<L'))
                image_len = struct.unpack('<L', byte_res)[0]

                image_stream = io.BytesIO()
                image_stream.write(self.connection.read(image_len))

                image_stream.seek(0)
                image_np = np.frombuffer(image_stream.getvalue(), dtype=np.uint8)
                image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

                while self.fq.qsize() > 1:
                    self.fq.get()
                self.fq.put(image)
                
                # Reset the reconnect delay upon a successful frame retrieval
                self.reconnect_delay = 2
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(self.reconnect_delay)  # Wait for the reconnect delay
                print(f"Reconnecting in {self.reconnect_delay} seconds")
                self.connect()  # Attempt to reconnect


cam2_fq = Queue()

# VideoCamera(cam2_fq, cam2_rq, 'rtsp://admin:admin@192.168.0.7/1')
def start_proc():
    VideoCamera(cam2_fq, '192.168.200.50', 8002)


cam_mapper = {
    # 'cam1': cam1_q,
    'cam2': cam2_fq
}

def gen(camq):
    while True:
        # print(frame)
        try:
            frame = camq.queue[0]
        except IndexError:
            frame = np.zeros((162, 296, 3), dtype=np.uint8)
  
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        # my_list = [frame, frame, frame]
        # list_bytes = json.dumps(my_list).encode('utf-8')
        # yield list_bytes
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@login_required
@gzip.gzip_page
def livestream_view(request, cam):
    global FLAG
    if FLAG:
        start_proc()
        FLAG = False
    try:
        # cam = VideoCamera()
        camq = cam_mapper[cam]
        response = StreamingHttpResponse(gen(camq), content_type="multipart/x-mixed-replace;boundary=frame")
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        raise e


@login_required
def cctv(request):
    com = Communication.objects.last()

    context = {
        'total': com.total_enable,
        'door': com.open_door
    }

    return render(request, 'cctv/mainpage.html', context=context)